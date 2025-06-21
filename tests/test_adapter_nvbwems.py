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

            result, is_closing = self.adapter.convert(situation)
            
            self.assertEqual('CONSTRUCTION', result['alert']['cause'])
            self.assertEqual('UNKNOWN_EFFECT', result['alert']['effect'])

    def test_SampleSituation2(self):

        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleSituation2.xml')
        with open(xml_filename, 'r') as xml_file:
            situation = fromstring(xml_file.read())

            result, is_closing = self.adapter.convert(situation)
            
            self.assertEqual('CONSTRUCTION', result['alert']['cause'])
            self.assertEqual('UNKNOWN_EFFECT', result['alert']['effect'])

    def test_SampleSituation3(self):

        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleSituation3.xml')
        with open(xml_filename, 'r') as xml_file:
            situation = fromstring(xml_file.read())

            result, is_closing = self.adapter.convert(situation)
            
            self.assertEqual('OTHER_CAUSE', result['alert']['cause'])
            self.assertEqual('DETOUR', result['alert']['effect'])

    def test_SampleSituation4(self):

        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleSituation4.xml')
        with open(xml_filename, 'r') as xml_file:
            situation = fromstring(xml_file.read())

            result, is_closing = self.adapter.convert(situation)
            
            self.assertEqual('MAINTENANCE', result['alert']['cause'])
            self.assertEqual('NO_SERVICE', result['alert']['effect'])
            