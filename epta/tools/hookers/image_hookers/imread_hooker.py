import cv2 as cv

from .base_image_hooker import BaseImageHooker


class ImreadHooker(BaseImageHooker):
    def __init__(self, name: str = 'imread_hooker', **kwargs):
        super(ImreadHooker, self).__init__(name=name, **kwargs)

    @staticmethod
    def hook_image(image_path: str, **kwargs) -> 'np.ndarray':
        image = cv.imread(image_path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        return image
