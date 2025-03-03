from vdv736.sirixml import get_elements as sirixml_get_elements
from vdv736.sirixml import get_value as sirixml_get_value
from vdv736.sirixml import get_attribute as sirixml_get_attribute
from vdv736.model import PublicTransportSituation

from ..adapter import BaseAdapter

class EmsAdapter(BaseAdapter):

    def __init__(self):
        pass

    def convert(self, public_transport_situation: PublicTransportSituation) -> dict:
        entity_id = sirixml_get_value(public_transport_situation, 'SituationNumber')

        alert_url = None
        alert_cause = self._convert_alert_cause(sirixml_get_value(public_transport_situation, 'AlertCause'))
        alert_effect = self._convert_alert_effect(sirixml_get_elements(public_transport_situation, 'Consequences'))
        alert_header_text = self._create_translated_string(
            sirixml_get_attribute(public_transport_situation, 'Summary.lang'),
            sirixml_get_value(public_transport_situation, 'Summary')
        )
        alert_description_text = self._create_translated_string(
            sirixml_get_attribute(public_transport_situation, 'Detail.lang'),
            sirixml_get_value(public_transport_situation, 'Detail')
        )


        # create result object
        result = {
            'entity_id': entity_id,
            'alert': {
                'url': alert_url,
                'cause': alert_cause,
                'effect': alert_effect,
                'header_text': alert_header_text,
                'desciption_text': alert_description_text
            }
        }

        # mark this element as deleted when the progress is 'closed'
        if sirixml_get_value(public_transport_situation, 'Progress', 'published') == 'closed':
            result['is_deleted'] = True

        # return result
        return result
    
    def _convert_alert_cause(self, cause: str) -> str:
        return 'UNKNOWN_CAUSE'

    def _convert_alert_effect(self, consequences) -> str:
        return 'UNKNOWN_EFFECT'

    def _create_translated_string(self, lang: str, text: str) -> dict:
        translated_string = dict()
        translated_string['translation'] = list()

        translated_string['translation'].append({
            'language': lang,
            'text': text
        })

        return translated_string