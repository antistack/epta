import abc

from epta.core import Tool


class Renderer(Tool, abc.ABC):
    def __init__(self, name: str = 'Renderer', **kwargs):
        super(Renderer, self).__init__(name=name, **kwargs)

    @abc.abstractmethod
    def render(self, *args, **kwargs):
        pass

    def use(self, *args, **kwargs):
        return self.render(*args, **kwargs)
