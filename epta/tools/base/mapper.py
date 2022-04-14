from .wrapper import ToolWrapper

class PositionMapperWrapper(ToolWrapper):
    """
    Wrapper for mappers to update positions if config was updated
    """

    def __init__(self, *args, **kwargs):
        super(PositionMapperWrapper, self).__init__(*args, **kwargs)

    def update(self, *args, **kwargs):
        # trigger tools update AND tools.use,
        # Because next, this will be used in 'global' position manager.
        self.tool.update(*args, **kwargs)
        self.use(*args, **kwargs)
