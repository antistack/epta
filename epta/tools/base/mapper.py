from epta.core import ToolDict

from epta.core.base_ops import *

def _wrap_update(self, fnc):
    def wrapper(*args, **kwargs):
        fnc(*args, **kwargs)
        self.update_key_mappings()
    return wrapper


class PositionMapper(ToolDict):
    def __init__(self, *args, **kwargs):
        super(PositionMapper, self).__init__(*args, **kwargs)
        self._key_mappings = tuple()

        self.update = _wrap_update(self, self.update)

    def update_key_mappings(self):
        self._key_mappings = tuple(
            key for key, value in self.items() if isinstance(value, BaseTool))

    def use(self, *args, **kwargs):  # just storing functions, no need to use as module
        pass

    def get_mapping_items(self, *args, **kwargs):
        return self.get_mapping_dict().items()

    def get_mapping_dict(self, *args, **kwargs) -> dict:
        ret = dict()
        for key in self._key_mappings:
            ret[key] = self[key]
        return ret


class PositionMapperWrapper(ToolDict):
    """
    Wrapper for mappers to update positions if config was updated
    """
    tool: PositionMapper

    def __init__(self, tool: PositionMapper, **kwargs):
        super(PositionMapperWrapper, self).__init__(**kwargs)
        self.tool = tool

    def use(self, *args, **kwargs):  # update cached values
        for key, value in self.tool.get_mapping_items():
            self[key] = value.use(*args, **kwargs)

    def update(self, *args, **kwargs):
        # trigger tools update AND tools.use,
        # Because next, this will be used in 'global' position manager.
        self.tool.update(*args, **kwargs)
        self.use(*args, **kwargs)
