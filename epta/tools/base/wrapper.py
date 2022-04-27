from epta.core import ToolDict


class ToolWrapper(ToolDict):
    """
    Wrapper to store tool values
    """

    def __init__(self, tool: 'ToolDict', name: str = None, **kwargs):
        self.tool = tool
        super(ToolWrapper, self).__init__(name=(name or tool.name), **kwargs)

    def use(self, *args, **kwargs):  # update cached values
        for key in self.tool:
            value = self.tool[key]
            self[key] = value.use(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.tool.update(*args, **kwargs)
