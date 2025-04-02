import logging
import pytz
import yaml

from .config import Configuration
from .repeatedtimer import RepeatedTimer

from datetime import datetime
from google.transit import gtfs_realtime_pb2
from google.protobuf.message import DecodeError
from google.protobuf.json_format import ParseDict
from math import floor
from paho.mqtt import client
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties
from vdv736.sirixml import get_elements as sirixml_get_elements
from vdv736.sirixml import get_value as sirixml_get_value
from vdv736.subscriber import Subscriber
from vdv736.delivery import SiriDelivery

class GtfsRealtimePublisher:

    def __init__(self, config_filename: str, host: str, port: str, username: str, password: str, topic: str, expiration: int) -> None:
        self._expiration = expiration
        
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
        if self._config['app']['adapter']['type'] == 'nvbw.ems':
            from .adapter.nvbw.ems import EmsAdapter
            self._adapter = EmsAdapter(self._config)
        else:
            raise ValueError(f"unknown adapter type {self._config['app']['adapter']['type']}")

        # connecto to MQTT broker as defined in config
        topic = topic.replace('+', '_')
        topic = topic.replace('#', '_')
        topic = topic.replace('$', '_')
        
        self._topic = topic

        self._mqtt = client.Client(client.CallbackAPIVersion.VERSION2, protocol=client.MQTTv5)

        if username is not None and password is not None:
            self._mqtt.username_pw_set(username=username, password=password)

        self._mqtt.connect(host, int(port))

    def run(self) -> None:
        if self._config['app']['pattern'] == 'publish/subscribe':
            
            # start subscriber with direct request mode
            with Subscriber(self._config['app']['subscriber'], self._config['app']['participants']) as subscriber:
                self._subscriber = subscriber
                self._subscriber.set_callbacks(self._subscriber_on_delivery)
                
                self._subscriber_status_timer = RepeatedTimer(self._config['app']['data_update_interval'], self._subscriber_status_request)
                self._subscriber_status_timer.start()
                
                try:
                    while True:
                        pass
                except KeyboardInterrupt:
                    self._subscriber_status_timer.stop()

        elif self._config['app']['pattern'] == 'request/response':
            
            # start subscriber using publish/subscribe mode
            with Subscriber(self._config['app']['subscriber'], self._config['app']['participants'], publish_subscribe=False) as subscriber:
                self._subscriber = subscriber
                self._subscriber.set_callbacks(self._subscriber_on_delivery)

                self._data_update_timer = RepeatedTimer(self._config['app']['data_update_interval'], self._subscriber_direct_request)
                self._data_update_timer.start_immediately()

                try:
                    while True:
                        pass
                except KeyboardInterrupt:
                    self._data_update_timer.stop()

                    self._mqtt.loop_stop()
                    self._mqtt.disconnect()

        else:
            raise ValueError(f"Unknown subscriber pattern {self._config['app']['pattern']}!")

    def _subscriber_status_request(self) -> None:
        if self._subscriber is not None:
            self._subscriber.status()

    def _subscriber_direct_request(self) -> None:
        if self._subscriber is not None:
            self._subscriber.request(self._config['app']['publisher'])

    def _subscriber_on_delivery(self, siri_delivery: SiriDelivery) -> None:
        timestamp = datetime.now().astimezone(pytz.timezone(self._config['app']['timezone'])).timestamp()
        timestamp = floor(timestamp)
        
        for situation in sirixml_get_elements(siri_delivery, 'Siri.ServiceDelivery.SituationExchangeDelivery.Situations.PtSituationElement'):
            alert_id = sirixml_get_value(situation, 'SituationNumber')
            
            # generate MQTT topic from placeholders
            # remove leading / if present, see #6 for reference
            topic = self._topic
            topic = topic.replace('[alertId]', alert_id)

            if topic.startswith('/'):
                topic = topic[1:]
            
            # generate feed message containing a single alert
            feed_message = dict()
            feed_message['header'] = {
                'gtfs_realtime_version': '2.0',
                'incrementality': 'DIFFERENTIAL',
                'timestamp': timestamp
            }

            feed_message['entity'] = list()
            
            # convert to PBF message and publish
            try:
                alert = self._adapter.convert(situation)

                feed_message['entity'].append({
                    'id': alert_id,
                    'alert': alert
                })

                pbf_object = gtfs_realtime_pb2.FeedMessage()
                ParseDict(feed_message, pbf_object)

                properties = Properties(PacketTypes.PUBLISH)
                properties.MessageExpiryInterval = self._expiration

                self._mqtt.publish(topic, pbf_object.SerializeToString(), 0, True, properties)

                logging.info(f"Published alert {alert_id}")

            except Exception as ex:
                logging.exception(ex) # TODO: remove this again
                logging.error(f"Could not convert situation {alert_id} due to an exception")

             