from epta.core import Tool


class Cropper(Tool):
    def __init__(self, name: str = 'Cropper', **kwargs):
        super(Cropper, self).__init__(name=name, **kwargs)

    @staticmethod
    def crop(image: 'np.ndarray', position: tuple, **__) -> dict:
        x_start, y_start, x_end, y_end = position
        crop = image[y_start:y_end, x_start:x_end]
        return crop

    def use(self, image: 'np.ndarray', position: tuple, **kwargs) -> dict:
        return self.crop(image, position)
