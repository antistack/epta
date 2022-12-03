import abc
from typing import Any

from epta.core import Tool


class Recogniser(Tool):
    """
    Tool to inherit from for more complex recognition tools.
    """
    def __init__(self, name: str = 'Recogniser', **kwargs):
        super(Recogniser, self).__init__(name=name, **kwargs)

    @abc.abstractmethod
    def image_to_data(self, *args, **kwargs) -> str:
        pass

    def use(self, *args, **kwargs) -> Any:
        return self.image_to_data(*args, **kwargs)
