import mss
import numpy as np
import cv2 as cv

from epta.core import PositionDependent

from .image_hooker import ImageHooker


class MssScreenHooker(ImageHooker, PositionDependent):
    def __init__(self, name: str = 'Mss_hooker', **kwargs):
        super(MssScreenHooker, self).__init__(name=name, **kwargs)

    def update(self, *args, **kwargs):
        x, y, x_end, y_end = self.make_single_position()
        w = x_end - x
        h = y_end - y
        self.inner_position = {"top": y, "left": x, "width": w, "height": h}

    def hook_image(self, *args, **kwargs) -> 'np.ndarray':
        with mss.mss() as sct:
            data = sct.grab(self.inner_position)
            img_array = np.array(data)[..., :3]
            img_array = cv.cvtColor(img_array, cv.COLOR_BGR2RGB)
        return img_array
