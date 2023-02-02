from typing import Any

from epta.core.meta import UpdateDependent


class Tool(UpdateDependent):
    """
    Base class for tool instance.

    Args:
        name (str): Tool name.
    """

    def __init__(self, name: str = 'Tool', **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def use(self, *args, **kwargs) -> Any:
        pass

    def update(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.use(*args, **kwargs)
