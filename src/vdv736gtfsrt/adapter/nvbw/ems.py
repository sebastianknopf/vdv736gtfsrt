from vdv736gtfsrt.adapter.vdv import VdvStandardAdapter
from vdv736gtfsrt.vdvdef import causes, conditions, effect_priorities
from vdv736gtfsrt.gtfsrt import create_url, create_translated_string, iso2unix

class EmsAdapter(VdvStandardAdapter):

    def _convert_alert_effect(self, consequences, map: dict|None = None) -> str:
        conditions_map = conditions
        conditions_map['noService'] = 'NO_SERVICE'
        
        return super()._convert_alert_effect(consequences, conditions_map)