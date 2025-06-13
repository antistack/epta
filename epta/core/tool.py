from typing import Any
import itertools
from epta.core.meta import UpdateDependent


class Tool(UpdateDependent):
    """
    Base class for tool instance.

    Args:
        name (str): Tool name. If None, a unique name will be generated.
    """
    _ids = itertools.count(0)

    def __init__(self, name: str = None, **kwargs):
        super().__init__(**kwargs)
        if name is None:
            self.name = f"{self.__class__.__name__}_{next(self._ids)}"
        else:
            self.name = name

    def use(self, *args, **kwargs) -> Any:
        pass

    def update(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.use(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
