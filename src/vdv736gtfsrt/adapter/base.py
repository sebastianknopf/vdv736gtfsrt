from abc import ABC, abstractmethod

from vdv736.model import PublicTransportSituation


class BaseAdapter(ABC):

    @abstractmethod
    def convert(self, public_transport_situation: PublicTransportSituation) -> tuple[dict, bool]:
        pass