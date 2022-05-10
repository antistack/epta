from epta.core import ToolDict


class ToolWrapper(ToolDict):
    """
    Stores :attr:`tool` values after use.

    Args:
        tool (ToolDict): Tool to store values from.
    """

    def __init__(self, tool: 'ToolDict', name: str = None, **kwargs):
        self.tool = tool
        super(ToolWrapper, self).__init__(name=(name or tool.name), **kwargs)

    def use(self, *args, **kwargs):  # update cached values
        for key in self.tool:
            value = self.tool[key]
            self[key] = value(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.tool.update(*args, **kwargs)

class PositionMapperWrapper(ToolWrapper):
    """
    Triggers ``use`` on ``update``.
    Used to wrap mappers. (for example, if config was updated)
    """

    def __init__(self, *args, **kwargs):
        super(PositionMapperWrapper, self).__init__(*args, **kwargs)

    def update(self, *args, **kwargs):
        # trigger tools update AND tools.use,
        # Because next, this will be used in 'global' position manager.
        self.tool.update(*args, **kwargs)
        self.use(*args, **kwargs)
