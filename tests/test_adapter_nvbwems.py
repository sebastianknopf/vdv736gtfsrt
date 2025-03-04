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

            self.assertEqual('ef478576-d1a8-527e-8820-5164ca986128', result['entity_id'])
            self.assertEqual('de', result['alert']['url']['translation'][0]['language'])
            self.assertEqual('https://yourdomain.com/alerts/de/ef478576-d1a8-527e-8820-5164ca986128', result['alert']['url']['translation'][0]['text'])
            
            self.assertEqual('CONSTRUCTION', result['alert']['cause'])
            self.assertEqual('UNKNOWN_EFFECT', result['alert']['effect'])

            self.assertEqual('de', result['alert']['header_text']['translation'][0]['language'])
            self.assertEqual('de', result['alert']['desciption_text']['translation'][0]['language'])

    def test_SampleSituation2(self):

        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleSituation2.xml')
        with open(xml_filename, 'r') as xml_file:
            situation = fromstring(xml_file.read())

            result = self.adapter.convert(situation)

            self.assertEqual('18acba15-9669-58af-91f1-7a0a3a9c3b98', result['entity_id'])
            self.assertEqual('de', result['alert']['url']['translation'][0]['language'])
            self.assertEqual('https://yourdomain.com/alerts/de/18acba15-9669-58af-91f1-7a0a3a9c3b98', result['alert']['url']['translation'][0]['text'])
            
            self.assertEqual('CONSTRUCTION', result['alert']['cause'])
            self.assertEqual('SIGNIFICANT_DELAYS', result['alert']['effect'])

            self.assertEqual('de', result['alert']['header_text']['translation'][0]['language'])
            self.assertEqual('de', result['alert']['desciption_text']['translation'][0]['language'])
            