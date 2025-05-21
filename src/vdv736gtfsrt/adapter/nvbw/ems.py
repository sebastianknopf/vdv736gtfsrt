from ..vdv import VdvStandardAdapter
from ..vdvdef import causes, conditions, effect_priorities
from ..gtfsrt import create_url, create_translated_string, iso2unix

class EmsAdapter(VdvStandardAdapter):

    def _convert_alert_effect(self, consequences, map: dict|None = None) -> str:
        conditions_map = conditions
        conditions_map[''] = 'UNKNOWN_EFFECT'
        
        return super()._convert_alert_effect(consequences, conditions_map)