from abc import ABC, abstractmethod


class AbstractClass(ABC):
    @abstractmethod
    def _get_schema(self):
        pass

    @abstractmethod
    def _validate(self):
        pass
