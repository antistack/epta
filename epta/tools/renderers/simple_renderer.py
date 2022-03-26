from .base_renderer import BaseRenderer

class SimpleRenderer(BaseRenderer):
    @staticmethod
    def render(*args, **kwargs):
        for arg in args:
            print(arg)
