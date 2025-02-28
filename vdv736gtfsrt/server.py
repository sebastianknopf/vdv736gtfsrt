import datetime
import json
import logging
import pytz
import yaml

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from google.transit import gtfs_realtime_pb2
from google.protobuf.message import DecodeError
from google.protobuf.json_format import ParseDict
from math import floor

class GtfsRealtimeServer:

    def __init__(self, config_filename: str) -> None:
    
        # load config and set default values
        with open(config_filename, 'r') as config_file:
            self._config = yaml.safe_load(config_file)

        self._config = self._default_config(self._config)

        # create adapter according to settings
        if self._config['app']['adapter']['type'] == 'nvbw.ems':
            from .adapter.nvbw.ems import EmsAdapter
            self._adapter = EmsAdapter()
        else:
            raise ValueError(f"unknown adapter type {self._config['app']['adapter']['type']}")

        # create API instance
        self._fastapi = FastAPI()
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

    async def _endpoint(self, request: Request) -> Response:
        
        # check whether there're cached data
        format = request.query_params['f'] if 'f' in request.query_params else 'pbf'

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

        # send response
        feed_message = self._create_feed_message(objects)
        if format  == 'json':
            json_result = json.dumps(feed_message, indent=4)

            if self._cache is not None:
                self._cache.set(f"{request.url.path}-{format}", json_result, self._config['caching']['caching_service_alerts_ttl_seconds'])

            return Response(content=json_result, media_type='application/json')
        else:
            pbf_result = ParseDict(feed_message, gtfs_realtime_pb2.FeedMessage()).SerializeToString()

            if self._cache is not None:
                self._cache.set(f"{request.url.path}-{format}", pbf_result, self._config['caching']['caching_service_alerts_ttl_seconds'])

            return Response(content=pbf_result, media_type='application/octet-stream')

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
    
    def _default_config(self, config):
        default_config = {
            'app': {
                'adapter': {
                    'type': 'nvbw.ems'
                },
                'endpoint': '/gtfsrt-service-alerts.pbf',
                'participants': 'participants.yaml',
                'caching_enabled': False
            },
            'caching': {
                'caching_server_endpoint': '[YourCachingServerEndpoint]',
                'caching_server_ttl_seconds': 120
            }
        }

        return self._merge_config(default_config, config)

    def _merge_config(self, defaults, actual):
        if isinstance(defaults, dict) and isinstance(actual, dict):
            return {k: self._merge_config(defaults.get(k, {}), actual.get(k, {})) for k in set(defaults) | set(actual)}
        
        return actual if actual else defaults

    def create(self) -> FastAPI:
        self._fastapi.include_router(self._api_router)

        return self._fastapi