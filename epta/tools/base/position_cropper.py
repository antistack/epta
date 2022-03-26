from epta.core import PositionDependent

from .cropper import Cropper

class PositionCropper(Cropper, PositionDependent):
    def __init__(self, name: str = 'PositionCropper', **kwargs):
        super(Cropper, self).__init__(name=name, **kwargs)

    def use(self, image: 'np.ndarray', *args, **kwargs) -> dict:
        return self.crop(image, self.inner_position)
