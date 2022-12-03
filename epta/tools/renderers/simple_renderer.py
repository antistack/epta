from .renderer import Renderer


class SimpleRenderer(Renderer):
    @staticmethod
    def render(*args, **kwargs):
        for arg in args:
            print(arg)
