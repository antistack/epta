from epta.core import ToolDict

from epta.core.base_ops import *

class ToolWrapper(ToolDict):
    """
    Wrapper to store tool values
    """

    def __init__(self, tool: 'ToolDict', **kwargs):
        super(ToolWrapper, self).__init__(name=tool.name, **kwargs)
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
        self.tool.update(*args, **kwargs)
        self.update_key_mappings()
