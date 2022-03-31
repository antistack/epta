from epta.core import ToolDict

from epta.core.base_ops import *

class PositionMapperWrapper(ToolDict):
    """
    Wrapper for mappers to update positions if config was updated
    """

    def __init__(self, tool: 'ToolDict', **kwargs):
        super(PositionMapperWrapper, self).__init__(name=tool.name, **kwargs)
        self.tool = tool
        self._key_mappings = tuple()

    def update_key_mappings(self):
        self._key_mappings = tuple(
            key for key, value in self.tool.items() if isinstance(value, BaseTool))

    def use(self, *args, **kwargs):  # update cached values
        for key in self._key_mappings:
            value = self.tool[key]
            self[key] = value.use(*args, **kwargs)

    def update(self, *args, **kwargs):
        # trigger tools update AND tools.use,
        # Because next, this will be used in 'global' position manager.
        self.tool.update(*args, **kwargs)
        self.update_key_mappings()
        self.use(*args, **kwargs)
