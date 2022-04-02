import cv2 as cv
import os
from typing import Union

def _save_crops(crops: Union[dict, 'np.ndarray'], save_path: str, prefix=''):
    # single leveled dictionary
    if isinstance(crops, dict):
        for name, crop in crops.items():
            _save_crops(crop, save_path, prefix=f'{prefix}_{name}')
    else:
        if crops is not None:
            if prefix.startswith('_'):
                prefix = prefix[1:]
            save_name = os.path.join(save_path, f'{prefix}.png')
            crop = cv.cvtColor(crops, cv.COLOR_RGB2BGR)
            cv.imwrite(save_name, crop)

def save_crops(crops: dict, save_path: str):
    # 2 leveled dictionary
    if not os.path.exists(temp := os.path.dirname(save_path)):
        os.makedirs(temp)
    _save_crops(crops, save_path)
