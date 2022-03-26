import cv2 as cv
import os


def save_crops(crops: dict, save_path: str, prefix=''):
    # single leveled dictionary
    for name, crop in crops.items():
        if crop is not None:
            save_name = os.path.join(save_path, f'{prefix}_{name}.png')
            crop = cv.cvtColor(crop, cv.COLOR_RGB2BGR)
            cv.imwrite(save_name, crop)

def save_2d_crops(crops: dict, save_path: str):
    # 2 leveled dictionary
    if not os.path.exists(temp := os.path.dirname(save_path)):
        os.makedirs(temp)
    for cropper_name in crops:
        save_crops(crops[cropper_name], save_path, prefix=cropper_name)
