import os
import unittest

from lxml.objectify import fromstring

from vdv736gtfsrt.adapter.vdv import VdvStandardAdapter

class VdvStandardAdapter_Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.adapter = VdvStandardAdapter({
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

            self.assertEqual('ef478576-d1a8-527e-8820-5164ca986128', result['id'])
            self.assertEqual('de', result['alert']['url']['translation'][0]['language'])
            self.assertEqual('https://yourdomain.com/alerts/de/ef478576-d1a8-527e-8820-5164ca986128', result['alert']['url']['translation'][0]['text'])
            
            self.assertEqual('CONSTRUCTION', result['alert']['cause'])
            self.assertEqual('UNKNOWN_EFFECT', result['alert']['effect'])

            self.assertEqual('de', result['alert']['header_text']['translation'][0]['language'])
            self.assertEqual('de', result['alert']['description_text']['translation'][0]['language'])

            self.assertEqual(1717984800, result['alert']['active_period'][0]['start'])
            self.assertNotIn('end', result['alert']['active_period'][0])

            self.assertEqual(1, len(result['alert']['informed_entity']))
            self.assertIn('stop_id', result['alert']['informed_entity'][0])
            self.assertEqual('8588794', result['alert']['informed_entity'][0]['stop_id'])
            self.assertIn('route_id', result['alert']['informed_entity'][0])
            self.assertEqual('85:37:62', result['alert']['informed_entity'][0]['route_id'])

            self.assertFalse(is_closing)

    def test_SampleSituation2(self):

        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleSituation2.xml')
        with open(xml_filename, 'r') as xml_file:
            situation = fromstring(xml_file.read())

            result, is_closing = self.adapter.convert(situation)

            self.assertEqual('18acba15-9669-58af-91f1-7a0a3a9c3b98', result['id'])
            self.assertEqual('de', result['alert']['url']['translation'][0]['language'])
            self.assertEqual('https://yourdomain.com/alerts/de/18acba15-9669-58af-91f1-7a0a3a9c3b98', result['alert']['url']['translation'][0]['text'])
            
            self.assertEqual('CONSTRUCTION', result['alert']['cause'])
            self.assertEqual('UNKNOWN_EFFECT', result['alert']['effect'])

            self.assertEqual('de', result['alert']['header_text']['translation'][0]['language'])
            self.assertEqual('de', result['alert']['description_text']['translation'][0]['language'])

            self.assertEqual(1728874800, result['alert']['active_period'][0]['start'])
            self.assertEqual(1730077200, result['alert']['active_period'][0]['end'])

            self.assertEqual(2, len(result['alert']['informed_entity']))
            self.assertIn('route_id', result['alert']['informed_entity'][0])
            self.assertNotIn('direction_id', result['alert']['informed_entity'][0])
            self.assertEqual('85:823:16', result['alert']['informed_entity'][0]['route_id'])
            self.assertIn('route_id', result['alert']['informed_entity'][1])
            self.assertNotIn('direction_id', result['alert']['informed_entity'][1])
            self.assertEqual('85:823:15', result['alert']['informed_entity'][1]['route_id'])

            self.assertFalse(is_closing)

    def test_SampleSituation3(self):

        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleSituation3.xml')
        with open(xml_filename, 'r') as xml_file:
            situation = fromstring(xml_file.read())

            result, is_closing = self.adapter.convert(situation)

            self.assertEqual(1748773800, result['alert']['active_period'][0]['start'])
            self.assertEqual(1748786400, result['alert']['active_period'][0]['end'])

            self.assertEqual(2, len(result['alert']['informed_entity']))

            self.assertIn('route_id', result['alert']['informed_entity'][0])
            self.assertIn('direction_id', result['alert']['informed_entity'][0])
            self.assertEqual('vpe:04734:_:H:j25', result['alert']['informed_entity'][0]['route_id'])
            self.assertEqual(0, result['alert']['informed_entity'][0]['direction_id'])

            self.assertIn('route_id', result['alert']['informed_entity'][1])
            self.assertIn('direction_id', result['alert']['informed_entity'][1])
            self.assertEqual('vpe:04734:_:R:j25', result['alert']['informed_entity'][1]['route_id'])
            self.assertEqual(1, result['alert']['informed_entity'][1]['direction_id'])

            self.assertFalse(is_closing)

    def test_SampleSituation4(self):

        xml_filename = os.path.join(os.path.dirname(__file__), 'data/xml/SampleSituation4.xml')
        with open(xml_filename, 'r') as xml_file:
            situation = fromstring(xml_file.read())

            result, is_closing = self.adapter.convert(situation)

            self.assertIn('route_id', result['alert']['informed_entity'][0])
            self.assertIn('direction_id', result['alert']['informed_entity'][0])
            self.assertIn('stop_id', result['alert']['informed_entity'][0])
            self.assertEqual('vpe:04720:_:H:j25', result['alert']['informed_entity'][0]['route_id'])
            self.assertEqual(0, result['alert']['informed_entity'][0]['direction_id'])
            self.assertEqual('7901106', result['alert']['informed_entity'][0]['stop_id'])

            self.assertTrue(is_closing)
            