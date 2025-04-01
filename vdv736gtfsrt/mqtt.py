from .config import Configuration
from .repeatedtimer import RepeatedTimer

from paho.mqtt import client
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties
from vdv736.subscriber import Subscriber
from vdv736.delivery import SiriDelivery

class GtfsRealtimePublisher:

    def __init__(self, config: dict, host: str, port: str, username: str, password: str, topic: str, expiration: int) -> None:
        self._config = Configuration.default_config(config)
        self._expiration = expiration

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
            with Subscriber(self._config['app']['subscriber'], self._config['app']['participants']) as subscriber:
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
        pass