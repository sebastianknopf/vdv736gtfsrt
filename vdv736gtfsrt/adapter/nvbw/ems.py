from typing import List
from vdv736.sirixml import get_elements as sirixml_get_elements
from vdv736.sirixml import get_value as sirixml_get_value
from vdv736.sirixml import get_attribute as sirixml_get_attribute
from vdv736.model import PublicTransportSituation

from ..adapter import BaseAdapter

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
        cause_map = {
            'unknown': 'UNKNOWN_CAUSE',
            'emergencyServicesCall': 'OTHER_CAUSE',
            'policeActivity': 'POLICE_ACTIVITY',
            'policeOrder': 'POLICE_ACTIVITY',
            'fire': 'OTHER_CAUSE',
            'cableFire': 'OTHER_CAUSE',
            'smokeDetectedOnVehicle': 'OTHER_CAUSE',
            'fireAtTheStation': 'OTHER_CAUSE',
            'fireRun': 'OTHER_CAUSE',
            'fireBrigadeOrder': 'OTHER_CAUSE',
            'explosion': 'OTHER_CAUSE',
            'explosionHazard': 'OTHER_CAUSE',
            'bombDisposal': 'OTHER_CAUSE',
            'emergencyMedicalServices': 'MEDICAL_EMERGENCY',
            'emergencyBrake': 'OTHER_CAUSE',
            'vandalism': 'OTHER_CAUSE',
            'cableTheft': 'OTHER_CAUSE',
            'signalPassedAtDanger': 'OTHER_CAUSE',
            'stationOverrun': 'OTHER_CAUSE',
            'passengersBlockingDoors': 'OTHER_CAUSE',
            'defectiveSecuritySystem': 'OTHER_CAUSE',
            'overcrowded': 'OTHER_CAUSE',
            'borderControl': 'POLICE_ACTIVITY',
            'unattendedBag': 'POLICE_ACTIVITY',
            'telephonedThreat': 'POLICE_ACTIVITY',
            'suspectVehicle': 'POLICE_ACTIVITY',
            'evacuation': 'POLICE_ACTIVITY',
            'terroristIncident': 'POLICE_ACTIVITY',
            'publicDisturbance': 'OTHER_CAUSE',
            'technicalProblem': 'TECHNICAL_PROBLEM',
            'vehicleFailure': 'TECHNICAL_PROBLEM',
            'serviceDisruption': 'OTHER_CAUSE',
            'doorFailure': 'TECHNICAL_PROBLEM',
            'lightingFailure': 'TECHNICAL_PROBLEM',
            'pointsProblem': 'TECHNICAL_PROBLEM',
            'signalProblem': 'TECHNICAL_PROBLEM',
            'signalFailure': 'TECHNICAL_PROBLEM',
            'overheadWireFailure': 'TECHNICAL_PROBLEM',
            'levelCrossingFailure': 'TECHNICAL_PROBLEM',
            'trafficManagementSystemFailure': 'TECHNICAL_PROBLEM',
            'engineFailure': 'TECHNICAL_PROBLEM',
            'repairWork': 'CONSTRUCTION',
            'constructionWork': 'CONSTRUCTION',
            'maintenanceWork': 'MAINTENANCE',
            'powerProblem': 'OTHER_CAUSE',
            'trackCircuitProblem': 'OTHER_CAUSE',
            'swingBridgeFailure': 'OTHER_CAUSE',
            'escalatorFailure': 'OTHER_CAUSE',
            'liftFailure': 'TECHNICAL_PROBLEM',
            'gangwayProblem': 'OTHER_CAUSE',
            'defectiveVehicle': 'TECHNICAL_PROBLEM',
            'brokenRail': 'OTHER_CAUSE',
            'poorRailConditions': 'OTHER_CAUSE',
            'deicingWork': 'OTHER_CAUSE',
            'wheelProblem': 'TECHNICAL_PROBLEM',
            'routeBlockage': 'OTHER_CAUSE',
            'congestion': 'OTHER_CAUSE',
            'heavyTraffic': 'OTHER_CAUSE',
            'routeDiversion': 'CONSTRUCTION',
            'unscheduledConstructionWork': 'CONSTRUCTION',
            'levelCrossingBlocked': 'OTHER_CAUSE',
            'sewerageMaintenance': 'MAINTENANCE',
            'roadClosed': 'OTHER_CAUSE',
            'roadwayDamage': 'OTHER_CAUSE',
            'bridgeDamage': 'OTHER_CAUSE',
            'personOnTheLine': 'OTHER_CAUSE',
            'objectOnTheLine': 'OTHER_CAUSE',
            'vehicleOnTheLine': 'OTHER_CAUSE',
            'animalOnTheLine': 'OTHER_CAUSE',
            'fallenTreeOnTheLine': 'WHEATHER',
            'vegetation': 'OTHER_CAUSE',
            'speedRestrictions': 'OTHER_CAUSE',
            'precedingVehicle': 'OTHER_CAUSE',
            'accident': 'ACCIDENT',
            'nearMiss': 'ACCIDENT',
            'personHitByVehicle': 'ACCIDENT',
            'vehicleStruckObject': 'ACCIDENT',
            'vehicleStruckAnimal': 'ACCIDENT',
            'derailment': 'ACCIDENT',
            'collision': 'ACCIDENT',
            'levelCrossingAccident': 'ACCIDENT',
            'poorWeather': 'WEATHER',
            'fog': 'WEATHER',
            'heavySnowfall': 'WEATHER',
            'heavyRain': 'WEATHER',
            'strongWinds': 'WEATHER',
            'ice': 'WEATHER',
            'hail': 'WEATHER',
            'highTemperatures': 'WEATHER',
            'flooding': 'WEATHER',
            'lowWaterLevel': 'WEATHER',
            'riskOfFlooding': 'WEATHER',
            'highWaterLevel': 'WEATHER',
            'fallenLeaves': 'WEATHER',
            'fallenTree': 'WEATHER',
            'landslide': 'WEATHER',
            'riskOfLandslide': 'WEATHER',
            'driftingSnow': 'WEATHER',
            'blizzardConditions': 'WEATHER',
            'stormDamage': 'WEATHER',
            'lightningStrike': 'WEATHER',
            'roughSea': 'WEATHER',
            'highTide': 'WEATHER',
            'lowTide': 'WEATHER',
            'iceDrift': 'WEATHER',
            'avalanches': 'WEATHER',
            'riskOfAvalanches': 'WEATHER',
            'flashFloods': 'WEATHER',
            'mudslide': 'WEATHER',
            'rockfalls': 'WEATHER',
            'subsidence': 'WEATHER',
            'earthquakeDamage': 'WEATHER',
            'grassFire': 'WEATHER',
            'wildlandFire': 'WEATHER',
            'iceOnRailway': 'WEATHER',
            'iceOnCarriages': 'WEATHER',
            'specialEvent': 'OTHER_CAUSE',
            'procession': 'DEMONSTRATION',
            'demonstration': 'DEMONSTRATION',
            'industrialAction': 'STRIKE',
            'staffSickness': 'OTHER_CAUSE',
            'staffAbsence': 'OTHER_CAUSE',
            'operatorCeasedTrading': 'OTHER_CAUSE',
            'previousDisturbances': 'OTHER_CAUSE',
            'vehicleBlockingTrack': 'OTHER_CAUSE',
            'foreignDisturbances': 'OTHER_CAUSE',
            'waitingForTransferPassengers': 'OTHER_CAUSE',
            'changeInCarriages': 'OTHER_CAUSE',
            'trainCoupling': 'OTHER_CAUSE',
            'boardingDelay': 'OTHER_CAUSE',
            'awaitingOncomingVehicle': 'OTHER_CAUSE',
            'overtaking': 'OTHER_CAUSE',
            'provisionDelay': 'OTHER_CAUSE',
            'miscellaneous': 'OTHER_CAUSE',
            'undefinedAlertCause': 'OTHER_CAUSE'
        }
        
        if cause in cause_map:
            return cause_map[cause]
        else:
            return 'UNKNOWN_CAUSE'

    def _convert_alert_effect(self, consequences) -> str:
        condition_map = {
            'unknown': 'UNKNOWN_EFFECT',
            'delay': 'SIGNIFICANT_DELAYS',
            'delayed': 'SIGNIFICANT_DELAYS', # NVBW specific, not VDV736!
            'minorDelays': 'SIGNIFICANT_DELAYS',
            'majorDelays': 'SIGNIFICANT_DELAYS',
            'operationTimeExtension': 'ADDITIONAL_SERVICE',
            'onTime': 'NO_EFFECT',
            'disturbanceRectified': 'NO_EFFECT',
            'changeOfPlatform': 'DETOUR',
            'lineCancellation': 'NO_SERVICE',
            'tripCancellation': 'NO_SERVICE',
            'boarding': 'NO_EFFECT',
            'goToGate': 'NO_EFFECT',
            'stopCancelled': 'NO_SERVICE',
            'stopMoved': 'STOP_MOVED',
            'stopOnDemand': 'MODIFIED_SERVICE',
            'additionalStop': 'ADDITIONAL_SERVICE',
            'substitutedStop': 'DETOUR',
            'diverted': 'DETOUR',
            'disruption': 'DETOUR',
            'limitedOperation': 'REDUCED_SERVICE',
            'discontinuedOperation': 'NO_SERVICE',
            'irregularTraffic': 'MODIFIED_SERVICE',
            'wagonOrderChanged': 'MODIFIED_SERVICE',
            'trainShortened': 'REDUCED_SERVICE',
            'additionalRide': 'ADDITIONAL_SERVICE',
            'replacementRide': 'MODIFIED_SERVICE',
            'temporaryStopplace': 'STOP_MOVED',
            'undefinedStatus': 'UNKNOWN_EFFECT'
        }

        # run through all consequences and convert conditions to effects
        effects = list()
        for consequence in consequences.Consequence:
            if consequence.Condition in condition_map:
                effects.append(condition_map[consequence.Condition])
            else:
                effects.append('UNKNOWN_EFFECT')

        # define order of effect priorities here
        effect_priorities = [
            'NO_SERVICE',
            'DETOUR',
            'STOP_MOVED',
            'REDUCED_SERVICE',
            'MODIFIED_SERVICE',
            'SIGNIFICANT_DELAYS',
            'ADDITIONAL_SERVICE',
            'ACCESSIBILITY_ISSUE',
            'OTHER_EFFECT',
            'NO_EFFECT',
            'UNKNOWN_EFFECT'
        ]

        # prioritize effects, as GTFS-RT spec allows only one effect actually
        if len(effects):
            return sorted(effects, key=lambda x: effect_priorities.index(x))[0]
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