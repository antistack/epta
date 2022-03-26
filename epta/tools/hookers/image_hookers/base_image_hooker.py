import abc

from epta.core import BaseTool


class BaseImageHooker(BaseTool, abc.ABC):
    def __init__(self, name: str = 'image_hooker', **kwargs):
        super(BaseImageHooker, self).__init__(name=name, **kwargs)

    def use(self, *args, **kwargs) -> dict:
        return self.hook_image(*args, **kwargs)

    @abc.abstractmethod
    def hook_image(self, *args, **kwargs) -> 'np.ndarray':
        pass
