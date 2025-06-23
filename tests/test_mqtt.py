import logging
import os
import responses
import threading
import unittest

from unittest.mock import patch

from vdv736gtfsrt.mqtt import GtfsRealtimePublisher

class GtfsRealtimePublisher_Test(unittest.TestCase):
    
    def setUp(self):

        self.responder = responses.RequestsMock()
        self.responder.start()

        # add first and second request (the same...) with a closing situation
        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleServiceDeliveryWithClosingSituation.xml')
        with open(xml_filename, 'r') as xml_file:
            xml_content = xml_file.read()

        self.responder.add(
            responses.POST,
            'http://127.0.0.1:9091/request',
            body=xml_content,
            content_type='application/xml',
            status=200
        )

        self.responder.add(
            responses.POST,
            'http://127.0.0.1:9091/request',
            body=xml_content,
            content_type='application/xml',
            status=200
        )

        # add third request with another situation ID in order to make the closing situation disappearing
        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleServiceDeliveryWithChangedSituationId.xml')
        with open(xml_filename, 'r') as xml_file:
            xml_content = xml_file.read()

        self.responder.add(
            responses.POST,
            'http://127.0.0.1:9091/request',
            body=xml_content,
            content_type='application/xml',
            status=200
        )

        # disable logging output
        logging.basicConfig(handlers=[logging.NullHandler()])

        return super().setUp()
    
    def test_ClosingSituation(self):
        
        # create mock helpers
        publish_feed_message_called: threading.Event = threading.Event()

        def publish_feed_message_patch(*args, **kws):
            feed_message: dict = args[1]

            if 'is_deleted' in feed_message['entity'][0] and feed_message['entity'][0]['is_deleted']:
                publish_feed_message_called.set()
                raise SystemExit()

        # create instance of GtfsRealtimePublisher and mock it up for testing
        publisher: GtfsRealtimePublisher = GtfsRealtimePublisher(
            './tests/data/yaml/test.yaml',
            'test.mosquitto.org',
            '1883',
            None,
            None,
            '/gtfs/realtime/servicealerts',
            300
        )

        # run publisher with testing patch
        with patch.object(publisher, '_publish_feed_message', side_effect=publish_feed_message_patch):
            thread: threading.Thread = threading.Thread(target=publisher.run)
            thread.start()

            publish_feed_message_called.wait(timeout=15)
            publisher.quit()

            self.assertTrue(publish_feed_message_called.is_set())            

    def tearDown(self):
        self.responder.stop()
        self.responder.reset()

        return super().tearDown()