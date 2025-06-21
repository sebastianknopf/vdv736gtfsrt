from vdv736.sirixml import get_elements as sirixml_get_elements
from vdv736.sirixml import get_value as sirixml_get_value
from vdv736.sirixml import get_attribute as sirixml_get_attribute
from vdv736.sirixml import exists as sirixml_exists
from vdv736.model import PublicTransportSituation

from vdv736gtfsrt.adapter.base import BaseAdapter
from vdv736gtfsrt.vdvdef import causes, conditions, effect_priorities
from vdv736gtfsrt.gtfsrt import create_url, create_translated_string, iso2unix

class VdvStandardAdapter(BaseAdapter):

    def __init__(self, config: dict) -> None:
        self._config = config

    def convert(self, public_transport_situation: PublicTransportSituation) -> tuple[dict, bool]:
        entity_id = sirixml_get_value(public_transport_situation, 'SituationNumber')

        alert_url = create_url(self._config['app']['adapter']['url'], alertId=entity_id)
        alert_cause = self._convert_alert_cause(sirixml_get_value(public_transport_situation, 'AlertCause'))
        alert_effect = self._convert_alert_effect(sirixml_get_elements(public_transport_situation, 'Consequences'))
        
        header_text = sirixml_get_value(public_transport_situation, 'Summary')
        if header_text is None:
            raise ValueError(f"Missing field 'Summary' for situation {entity_id}")
        
        alert_header_text = create_translated_string(
            [sirixml_get_attribute(public_transport_situation, 'Summary.{http://www.w3.org/XML/1998/namespace}lang', 'de')],
            [header_text]
        )

        description_text = sirixml_get_value(public_transport_situation, 'Detail')
        if description_text is None:
            raise ValueError(f"Missing field 'Detail' for situation {entity_id}")
        
        alert_description_text = create_translated_string(
            [sirixml_get_attribute(public_transport_situation, 'Detail.{http://www.w3.org/XML/1998/namespace}lang', 'de')],
            [description_text]
        )

        alert_active_periods = self._convert_active_periods(public_transport_situation)
        alert_informed_entities = self._convert_informed_entities(public_transport_situation)

        # create result object
        result = {
            'id': entity_id,
            'alert': {
                'url': alert_url,
                'cause': alert_cause,
                'effect': alert_effect,
                'header_text': alert_header_text,
                'description_text': alert_description_text,
                'active_period': alert_active_periods,
                'informed_entity': alert_informed_entities
            }
        }

        # mark this element as deleted when the progress is 'closed'
        if sirixml_get_value(public_transport_situation, 'Progress', 'published') == 'closed':
            result['is_deleted'] = True

        # return result and the boolean indicator whether the event is closing currently or not
        return result, sirixml_get_value(public_transport_situation, 'Progress', 'published') == 'closing'
    
    def _convert_active_periods(self, public_transport_situation: PublicTransportSituation) -> list:
        active_periods = list()

        for validity_period in public_transport_situation.ValidityPeriod:
            start_time = sirixml_get_value(validity_period, 'StartTime')
            end_time = sirixml_get_value(validity_period, 'EndTime')

            active_period = dict()
            if start_time is not None:
                active_period['start'] = iso2unix(start_time)
            
            if end_time is not None and not end_time.startswith('2500'):
                active_period['end'] = iso2unix(end_time)

            if len(active_period.keys()) > 0:
                active_periods.append(active_period)

        return active_periods

    def _convert_informed_entities(self, public_transport_situation: PublicTransportSituation) -> list:
        informed_entities = list()
        
        for consequence in sirixml_get_elements(public_transport_situation, 'Consequences.Consequence'):
            if sirixml_exists(consequence, 'Affects.Networks'):
                for network in sirixml_get_elements(consequence, 'Affects.Networks.AffectedNetwork'):
                    for line in sirixml_get_elements(network, 'AffectedLine'):
                        direction_id = sirixml_get_value(line, 'Direction.DirectionRef', None)
                        if direction_id is not None:
                            direction_id = self._convert_direction_id(direction_id)
                            informed_entities.append({
                                'route_id': sirixml_get_value(line, 'LineRef', None),
                                'direction_id': direction_id
                            })
                        else:
                            informed_entities.append({
                                'route_id': sirixml_get_value(line, 'LineRef', None)
                            })

            elif sirixml_exists(consequence, 'Affects.StopPlaces'):
                for stop_place in sirixml_get_elements(consequence, 'Affects.StopPlaces.AffectedStopPlace'):
                    stop_id = sirixml_get_value(stop_place, 'StopPlaceRef', None)

                    if sirixml_exists(stop_place, 'Lines.AffectedLine'):
                        for stop_place_line in sirixml_get_elements(stop_place, 'Lines.AffectedLine'):
                            direction_id = sirixml_get_value(stop_place_line, 'Direction.DirectionRef', None)
                            if direction_id is not None:
                                direction_id = self._convert_direction_id(direction_id)
                                informed_entities.append({
                                    'route_id': sirixml_get_value(stop_place_line, 'LineRef', None),
                                    'stop_id': stop_id,
                                    'direction_id': direction_id
                                })
                            else:
                                informed_entities.append({
                                    'route_id': sirixml_get_value(stop_place_line, 'LineRef'),
                                    'stop_id': stop_id
                                })
                    else:
                        informed_entities.append({
                            'stop_id': stop_id
                        })

            elif sirixml_exists(consequence, 'Affects.StopPoints'):
                for stop_point in sirixml_get_elements(consequence, 'Affects.StopPoints.AffectedStopPoint'):
                    stop_id = sirixml_get_value(stop_place, 'StopPointRef', None)

                    if sirixml_exists(stop_point, 'Lines.AffectedLine'):
                        for stop_place_line in sirixml_get_elements(stop_place, 'Lines.AffectedLine'):
                            informed_entities.append({
                                'route_id': sirixml_get_value(stop_place_line, 'LineRef'),
                                'stop_id': stop_id
                            })
                    else:
                        informed_entities.append({
                            'stop_id': stop_id
                        })
            elif sirixml_exists(consequence, 'Affects.Operators'):
                for operator in sirixml_get_elements(consequence, 'Affects.Operators'):
                    informed_entities.append({
                        'agency_id': sirixml_get_value(operator, 'OperatorRef')
                    })

        return informed_entities
    
    def _convert_alert_cause(self, cause: str, map: dict|None = None) -> str:
        if map is not None and len(map) > 0:
            cause_map = map
        else:
            cause_map = causes
        
        if cause in cause_map:
            return cause_map[cause]
        else:
            return 'UNKNOWN_CAUSE'

    def _convert_alert_effect(self, consequences, map: dict|None = None) -> str:
        if map is not None and len(map) > 0:
            condition_map = map
        else:
            condition_map = conditions

        # run through all consequences and convert conditions to effects
        effects = list()
        for consequence in consequences.Consequence:
            if sirixml_exists(consequence, 'Condition') and consequence.Condition in condition_map:
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
        
    def _convert_direction_id(self, direction_id: str) -> int:
        direction_id = direction_id \
            .replace('1', '0') \
            .replace('2', '0') \
            .replace('H', '0') \
            .replace('h', '0') \
            .replace('R', '1') \
            .replace('r', '1')
        
        direction_id = int(direction_id)

        return direction_id
