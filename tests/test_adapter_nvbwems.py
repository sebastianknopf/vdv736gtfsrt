import os
import unittest

from lxml.objectify import fromstring

from vdv736gtfsrt.adapter.nvbw.ems import EmsAdapter

class Adapter_NvbwEms_Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.adapter = EmsAdapter({
            'app': {
                'adapter': {
                    'url': {
                        'de': 'https://yourdomain.com/alerts/de/[alertId]'
                    }
                }
            }
        })

    def test_SampleSituation1(self):

        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleSituation1.xml')
        with open(xml_filename, 'r') as xml_file:
            situation = fromstring(xml_file.read())

            result = self.adapter.convert(situation)
            
            self.assertEqual('UNKNOWN_CAUSE', result['alert']['cause'])
            self.assertEqual('UNKNOWN_EFFECT', result['alert']['effect'])

    def test_SampleSituation2(self):

        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleSituation2.xml')
        with open(xml_filename, 'r') as xml_file:
            situation = fromstring(xml_file.read())

            result = self.adapter.convert(situation)
            
            self.assertEqual('UNKNOWN_CAUSE', result['alert']['cause'])
            self.assertEqual('UNKNOWN_EFFECT', result['alert']['effect'])
            