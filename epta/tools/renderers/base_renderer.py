import abc

from epta.core import BaseTool


class BaseRenderer(BaseTool, abc.ABC):
    def __init__(self, name: str = 'base_renderer', **kwargs):
        super(BaseRenderer, self).__init__(name=name, **kwargs)

    @abc.abstractmethod
    def render(self, *args, **kwargs):
        pass

    def use(self, *args, **kwargs):
        return self.render(*args, **kwargs)
