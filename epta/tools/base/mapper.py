from epta.core import *
from epta.core.base_ops import *


class PositionMapper(BaseTool, ConfigDependent):
    def __init__(self, config: 'Config', key_mappings: tuple = tuple(), **kwargs):
        super(PositionMapper, self).__init__(config=config, **kwargs)
        self._key_mappings = key_mappings

    def update_mapping_names(self):
        # TODO: move this keys to properties?
        self._key_mappings = tuple(
            key for key in self.__dict__ if key not in {'name', 'config', '_key_mappings', 'tool'})

    def use(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        self.update_mapping_names()
        self.use(*args, **kwargs)

    def get_mapping_items(self, *args, **kwargs):
        return self.get_mapping_dict().items()

    def get_mapping_dict(self, *args, **kwargs) -> dict:
        ret = dict()
        for key in self._key_mappings:
            value = getattr(self, key)
            ret[key] = value
        return ret


class PositionMapperWrapper(PositionMapper, Wrapper):
    """
    Wrapper for mappers to update positions if config was updated
    """
    tool: PositionMapper

    def __init__(self, tool: PositionMapper, **kwargs):
        super(PositionMapperWrapper, self).__init__(config=tool.config, name=tool.name, tool=tool,
                                                    key_mappings=tool._key_mappings, **kwargs)

    @property
    def key_mappings(self) -> tuple:
        return self.tool._key_mappings

    def update(self, *args, **kwargs):
        self.tool.update()
        for key, value in self.tool.get_mapping_items():
            setattr(self, key, value(self.config))
