from datetime import datetime
from typing import List
from vdv736.sirixml import get_elements as sirixml_get_elements
from vdv736.sirixml import get_value as sirixml_get_value
from vdv736.sirixml import get_attribute as sirixml_get_attribute
from vdv736.sirixml import exists as sirixml_exists
from vdv736.model import PublicTransportSituation

from ..adapter import BaseAdapter
from ..vdvdef import causes, conditions, effect_priorities

class EmsAdapter(BaseAdapter):

    def __init__(self, config: dict) -> None:
        self._config = config

    def convert(self, public_transport_situation: PublicTransportSituation) -> dict:
        entity_id = sirixml_get_value(public_transport_situation, 'SituationNumber')

        alert_url = self._create_alert_url(alertId=entity_id)
        alert_cause = self._convert_alert_cause(sirixml_get_value(public_transport_situation, 'AlertCause'))
        alert_effect = self._convert_alert_effect(sirixml_get_elements(public_transport_situation, 'Consequences'))
        alert_header_text = self._create_translated_string(
            [sirixml_get_attribute(public_transport_situation, 'Summary.{http://www.w3.org/XML/1998/namespace}lang', 'de')],
            [sirixml_get_value(public_transport_situation, 'Summary')]
        )
        alert_description_text = self._create_translated_string(
            [sirixml_get_attribute(public_transport_situation, 'Detail.{http://www.w3.org/XML/1998/namespace}lang', 'de')],
            [sirixml_get_value(public_transport_situation, 'Detail')]
        )

        alert_active_periods = list()
        for publication_window in public_transport_situation.PublicationWindow:
            start_time = sirixml_get_value(publication_window, 'StartTime')
            end_time = sirixml_get_value(publication_window, 'EndTime')

            active_period = dict()
            if start_time is not None:
                active_period['start'] = self._iso2unix(start_time)
            
            if end_time is not None and not end_time.startswith('2500'):
                active_period['end'] = self._iso2unix(end_time)

            if len(active_period.keys()) > 0:
                alert_active_periods.append(active_period)

        alert_informed_entities = list()
        for publishing_action in sirixml_get_elements(public_transport_situation, 'PublishingActions.PublishingAction'):
            if publishing_action.PublishAtScope.ScopeType == 'stopPlace':
                
                for stop_place in sirixml_get_elements(publishing_action, 'PublishAtScope.Affects.StopPlaces.AffectedStopPlace'):
                    entity_selector = {
                        'stop_id': sirixml_get_value(stop_place, 'StopPlaceRef')
                    }

                    if sirixml_exists(stop_place, 'Lines.AffectedLine'):
                        for line in stop_place.Lines.AffectedLine:
                            entity_selector['route_id'] = sirixml_get_value(line, 'LineRef')

                    alert_informed_entities.append(entity_selector)

            elif publishing_action.PublishAtScope.ScopeType == 'stopPoint':
                pass
            elif publishing_action.PublishAtScope.ScopeType == 'stopPlaceComponent':
                pass
            elif publishing_action.PublishAtScope.ScopeType == 'line':
                
                for network in sirixml_get_elements(publishing_action, 'PublishAtScope.Affects.Networks.AffectedNetwork'):
                    if sirixml_exists(network, 'AffectedLine'):
                        for line in sirixml_get_elements(network, 'AffectedLine'):
                            entity_selector = {
                                'route_id': sirixml_get_value(line, 'LineRef')
                            }

                            alert_informed_entities.append(entity_selector)

            elif publishing_action.PublishAtScope.ScopeType == 'route':
                pass
            elif publishing_action.PublishAtScope.ScopeType == 'operator':
                pass
            elif publishing_action.PublishAtScope.ScopeType == 'place':
                pass
            elif publishing_action.PublishAtScope.ScopeType == 'network':
                pass
            elif publishing_action.PublishAtScope.ScopeType == 'vehicleJourney':
                pass
            elif publishing_action.PublishAtScope.ScopeType == 'datedVehicleJourney':
                pass
            elif publishing_action.PublishAtScope.ScopeType == 'connectionLink':
                pass
            elif publishing_action.PublishAtScope.ScopeType == 'interchange':
                pass
            elif publishing_action.PublishAtScope.ScopeType == 'allPT' or publishing_action.PublishAtScope.ScopeType == 'general':
                pass

        # create result object
        result = {
            'entity_id': entity_id,
            'alert': {
                'url': alert_url,
                'cause': alert_cause,
                'effect': alert_effect,
                'header_text': alert_header_text,
                'desciption_text': alert_description_text,
                'active_period': alert_active_periods,
                'informed_entity': alert_informed_entities
            }
        }

        # mark this element as deleted when the progress is 'closed'
        if sirixml_get_value(public_transport_situation, 'Progress', 'published') == 'closed':
            result['is_deleted'] = True

        # return result
        return result
    
    def _convert_alert_cause(self, cause: str) -> str:
        cause_map = causes
        
        if cause in cause_map:
            return cause_map[cause]
        else:
            return 'UNKNOWN_CAUSE'

    def _convert_alert_effect(self, consequences) -> str:
        condition_map = conditions
        condition_map['delayed'] = 'SIGNIFICANT_DELAYS'

        # run through all consequences and convert conditions to effects
        effects = list()
        for consequence in consequences.Consequence:
            if consequence.Condition in condition_map:
                effects.append(condition_map[consequence.Condition])
            else:
                effects.append('UNKNOWN_EFFECT')

        # define order of effect priorities here
        prios = effect_priorities

        # prioritize effects, as GTFS-RT spec allows only one effect actually
        if len(effects):
            return sorted(effects, key=lambda x: prios.index(x))[0]
        else:
            return 'UNKNOWN_EFFECT'

    def _create_alert_url(self, **variables) -> dict:
         
        languages = list()
        texts = list()
        for lang, template in self._config['app']['adapter']['url'].items():
            url = template
            for key, value in variables.items():
                tkey = f"[{key}]"
                url = url.replace(tkey, value)

            languages.append(lang)
            texts.append(url)
        
        return self._create_translated_string(languages, texts)

    def _create_translated_string(self, languages: List[str], texts: List[str]) -> dict:
        translated_string = dict()
        translated_string['translation'] = list()

        if len(languages) != len(texts):
            raise ValueError('the number of languages must be the same like the number of texts')
        
        for n in range(0, len(languages)):
            translated_string['translation'].append({
                'language': languages[n].lower(),
                'text': texts[n]
            })

        return translated_string
    
    def _iso2unix(self, iso_timestamp: str) -> int:
        dt = datetime.strptime(iso_timestamp, '%Y-%m-%dT%H:%M:%SZ')
        return int((dt - datetime(1970, 1, 1)).total_seconds())