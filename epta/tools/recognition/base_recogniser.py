import abc
from typing import Any

from epta.core import BaseTool


class BaseRecogniser(BaseTool):
    """
    Tool to inherit from for more complex recognition tools.
    """
    def __init__(self, name: str = 'base_recogniser', **kwargs):
        super(BaseRecogniser, self).__init__(name=name, **kwargs)

    @abc.abstractmethod
    def image_to_data(self, *args, **kwargs) -> str:
        pass

    def use(self, *args, **kwargs) -> Any:
        return self.image_to_data(*args, **kwargs)
