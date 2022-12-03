import cv2 as cv

from .image_hooker import ImageHooker


class ImreadHooker(ImageHooker):
    def __init__(self, name: str = 'Imread_hooker', **kwargs):
        super(ImreadHooker, self).__init__(name=name, **kwargs)

    @staticmethod
    def hook_image(image_path: str, **kwargs) -> 'np.ndarray':
        image = cv.imread(image_path)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        return image
