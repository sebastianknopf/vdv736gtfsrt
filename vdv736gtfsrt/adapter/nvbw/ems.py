from ..vdv import VdvStandardAdapter
from ..vdvdef import causes, conditions, effect_priorities
from ..gtfsrt import create_url, create_translated_string, iso2unix

class EmsAdapter(VdvStandardAdapter):

    def _convert_alert_cause(self, cause: str) -> str:
        """cause_map = causes
        
        if cause in cause_map:
            return cause_map[cause]
        else:
            return 'UNKNOWN_CAUSE'"""
        
        return 'CONSTRUCTION'

    def _convert_alert_effect(self, consequences) -> str:
        """condition_map = conditions
        condition_map['delayed'] = 'SIGNIFICANT_DELAYS'

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
            return 'UNKNOWN_EFFECT'"""
        
        return 'SIGNIFICANT_DELAYS'