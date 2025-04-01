from ..vdv import VdvStandardAdapter
from ..vdvdef import causes, conditions, effect_priorities
from ..gtfsrt import create_url, create_translated_string, iso2unix

class EmsAdapter(VdvStandardAdapter):

    def _convert_alert_cause(self, cause: str) -> str:
        return 'UNKNOWN_CAUSE'

    def _convert_alert_effect(self, consequences) -> str:
        return 'UNKNOWN_EFFECT'