import json
import logging
import pytz
import yaml

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from google.transit import gtfs_realtime_pb2
from google.protobuf.message import DecodeError
from google.protobuf.json_format import ParseDict
from math import floor
from vdv736.subscriber import Subscriber

from .config import Configuration
from .repeatedtimer import RepeatedTimer

class GtfsRealtimeServer:

    def __init__(self, config_filename: str) -> None:
    
        # load config and set default values
        with open(config_filename, 'r') as config_file:
            self._config = yaml.safe_load(config_file)

        self._config = Configuration.default_config(self._config)

        # check for required non-default configs
        if 'app' not in self._config:
            raise ValueError("required config key 'app' missing")
        
        if 'adapter' not in self._config['app']:
            raise ValueError("required config key 'app.adapter' missing")

        if 'type' not in self._config['app']['adapter']:
            raise ValueError("required config key 'app.adapter.type' missing")
        
        if 'url' not in self._config['app']['adapter']:
            raise ValueError("required config key 'app.adapter.url' missing")

        if 'participants' not in self._config['app']:
            raise ValueError("required config key 'app.participants' missing")
        
        if 'subscriber' not in self._config['app']:
            raise ValueError("required config key 'app.subscriber' missing")
        
        if 'publisher' not in self._config['app']:
            raise ValueError("required config key 'app.publisher' missing")
        
        if 'pattern' not in self._config['app']:
            raise ValueError("required config key 'app.pattern' missing")

        # create adapter according to settings
        if self._config['app']['adapter']['type'] == 'vdv':
            from .adapter.vdv import VdvStandardAdapter
            self._adapter = VdvStandardAdapter(self._config)
        elif self._config['app']['adapter']['type'] == 'nvbw.ems':
            from .adapter.nvbw.ems import EmsAdapter
            self._adapter = EmsAdapter(self._config)
        else:
            raise ValueError(f"unknown adapter type {self._config['app']['adapter']['type']}")

        # create API instance
        self._fastapi = FastAPI(lifespan=self._lifespan)
        self._api_router = APIRouter()

        self._api_router.add_api_route(
            self._config['app']['endpoint'], 
            endpoint=self._endpoint, 
            methods=['GET']
        )

        # enable chaching if configured
        if 'caching_enabled' in self._config['app'] and self._config['app']['caching_enabled'] == True:
            import memcache

            self._cache = memcache.Client([self._config['caching']['caching_server_endpoint']], debug=0)
            self._cache_ttl = self._config['caching']['caching_server_ttl_seconds']
        else:
            self._cache = None

        # create logger instance
        self._logger = logging.getLogger('uvicorn')

        # class container for subscriber
        self._subscriber = None
        self._subscriber_status_timer = None
        self._subscriber_data_update_timer = None

    @asynccontextmanager
    async def _lifespan(self, app):
        
        # set datalog directory
        datalog = './datalog' if self._config['app']['datalog_enabled'] else None
        
        if self._config['app']['pattern'] == 'publish/subscribe':
            
            # start subscriber using publish/subscribe mode
            with Subscriber(self._config['app']['subscriber'], self._config['app']['participants'], datalog_directory=datalog) as subscriber:
                self._subscriber = subscriber

                # subscribe at the defined publisher
                self._subscriber.subscribe(self._config['app']['publisher'])

                # start internal repeated timer for subscriber's status requests
                self._subscriber_status_timer = RepeatedTimer(self._config['app']['status_request_interval'], self._subscriber_status_request)
                self._subscriber_status_timer.start()

                # wait here for GtfsRealtimeServer server's termination
                yield

                self._logger.info('Shutting down GtfsRealtimeServer')

                # terminate subscribers status timer
                self._subscriber_status_timer.stop()

                # all subscriptions will terminate while exiting the context of 
                # the subscriber - no need to do anything else here

        elif self._config['app']['pattern'] == 'request/response':
            
            # start subscriber with direct request mode
            with Subscriber(self._config['app']['subscriber'], self._config['app']['participants'], publish_subscribe=False, datalog_directory=datalog) as subscriber:
                self._subscriber = subscriber

                # start internal repeated timer for subscriber's data direct request
                self._subscriber_data_update_timer = RepeatedTimer(self._config['app']['data_update_interval'], self._subscriber_direct_request)
                self._subscriber_data_update_timer.start_immediately()

                # wait here for GtfsRealtimeServer server's termination
                yield

                self._logger.info('Shutting down GtfsRealtimeServer')

                # terminate subscribers status timer
                self._subscriber_data_update_timer.stop()

        else:
            raise ValueError(f"Unknown subscriber pattern {self._config['app']['pattern']}!")

    async def _endpoint(self, request: Request) -> Response:
        
        # check whether there're cached data
        format = 'json' if 'debug' in request.query_params else 'pbf'

        if self._cache is not None:
            cached_response = self._cache.get(f"{request.url.path}-{format}")
            if cached_response is not None:
                if format == 'json':
                    mime_type = 'application/json'
                else:
                    mime_type = 'application/octet-stream'

                return Response(content=cached_response, media_type=mime_type)
            
        # render objects out of current messages
        objects = []
        for situation_id, situation in self._subscriber.get_situations().items():
            try:
                conversion: tuple[dict, bool] = self._adapter.convert(situation)
                alert, is_closing = conversion

                # special handling for closing situations
                # see #26 for more information
                if is_closing:                
                    # set effect to NO_EFFECT and delete end timestamps of active periods in order to make consuming systems
                    # to show up the final message without affecting the trip planning system
                    # see #26 for more information
                    alert['effect'] = 'NO_EFFECT'
                    for active_period in alert['active_period']:
                        if 'end' in active_period:
                            del active_period['end']

                if alert is not None:
                    objects.append(alert)
            except Exception as ex:
                self._logger.error(ex)

        # send response
        feed_message = self._create_feed_message(objects)
        if format  == 'json':
            json_result = json.dumps(feed_message, indent=4, ensure_ascii=False)

            if self._cache is not None:
                self._cache.set(f"{request.url.path}-{format}", json_result, self._config['caching']['caching_service_alerts_ttl_seconds'])

            return Response(content=json_result, media_type='application/json')
        else:
            pbf_result = ParseDict(feed_message, gtfs_realtime_pb2.FeedMessage()).SerializeToString()

            if self._cache is not None:
                self._cache.set(f"{request.url.path}-{format}", pbf_result, self._config['caching']['caching_service_alerts_ttl_seconds'])

            return Response(content=pbf_result, media_type='application/octet-stream')

    def _subscriber_status_request(self):
        if self._subscriber is not None:
            self._subscriber.status()

    def _subscriber_direct_request(self):
        if self._subscriber is not None:
            self._subscriber.request(self._config['app']['publisher'])
    
    def _create_feed_message(self, entities):
        timestamp = datetime.now().astimezone(pytz.timezone(self._config['app']['timezone'])).timestamp()
        timestamp = floor(timestamp)
        
        return {
            'header': {
                'gtfs_realtime_version': '2.0',
                'incrementality': 'FULL_DATASET',
                'timestamp': timestamp
            },
            'entity': entities
        }

    def create(self) -> FastAPI:
        self._fastapi.include_router(self._api_router)

        return self._fastapi