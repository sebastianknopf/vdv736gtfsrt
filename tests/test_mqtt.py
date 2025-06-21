import os
import responses
import unittest

from lxml.objectify import fromstring

from vdv736gtfsrt.mqtt import GtfsRealtimePublisher

class GtfsRealtimePublisher_Test(unittest.TestCase):
    
    def setUp(self):
        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleServiceDelivery.xml')
        with open(xml_filename, 'r') as xml_file:
            xml_content = xml_file.read()
        
        self.responder = responses.RequestsMock(assert_all_requests_are_fired=False)
        self.responder.start()

        self.responder.add(
            responses.POST,
            'http://127.0.0.1:9091/request',
            body=xml_content,
            content_type='application/xml',
            status=200
        )

        return super().setUp()
    
    def test_SampleSituation1(self):
        publisher: GtfsRealtimePublisher = GtfsRealtimePublisher(
            './tests/data/yaml/test.yaml',
            'test.mosquitto.org',
            '1883',
            None,
            None,
            '/gtfs/realtime/servicealerts',
            300
        )

        publisher.run()

    def tearDown(self):
        self.responder.stop()
        self.responder.reset()

        return super().tearDown()