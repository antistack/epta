import abc

from epta.core import Tool


class ImageHooker(Tool, abc.ABC):
    def __init__(self, name: str = 'Image_hooker', **kwargs):
        super(ImageHooker, self).__init__(name=name, **kwargs)

    def use(self, *args, **kwargs) -> dict:
        return self.hook_image(*args, **kwargs)

    @abc.abstractmethod
    def hook_image(self, *args, **kwargs) -> 'np.ndarray':
        pass
