import os
from datetime import datetime

import cv2
import numpy as np

_RESOURCE_DIR_PATH = r'resources'
_RAW_DIR_PATH = os.path.join(_RESOURCE_DIR_PATH, r'dataset\raw')
_RAW_DATA_PATH = os.path.join(_RAW_DIR_PATH, 'raw.npy')

_IMAGE_OUTPUT_DIR_PATH = os.path.join(_RAW_DIR_PATH, r'lmb')
_FULL_IMAGE_DIR_PATH = os.path.join(_IMAGE_OUTPUT_DIR_PATH, r'full')
_SMALL_IMAGE_DIR_PATH = os.path.join(_IMAGE_OUTPUT_DIR_PATH, r'small')
_FINAL_IMAGE_DIR_PATH = os.path.join(_IMAGE_OUTPUT_DIR_PATH, r'final')


def output_full_image():
    if not os.path.exists(_RAW_DATA_PATH):
        return

    images = np.load(_RAW_DATA_PATH, allow_pickle=True)[1:-1]
    print(f'raw images count: {len(images)}')

    batch_id = (datetime.now() - datetime(2021, 10, 10)).total_seconds()
    for i, image in enumerate(images):
        path = os.path.join(_FULL_IMAGE_DIR_PATH, f'{batch_id}-{i}.png')
        cv2.imwrite(path, image)

    os.remove(_RAW_DATA_PATH)


def convert_full_image_to_small_image():
    full_image_names = os.listdir(_FULL_IMAGE_DIR_PATH)

    default_pos = None
    default_size = None

    for full_image_name in full_image_names:
        small_image_path = os.path.join(_SMALL_IMAGE_DIR_PATH, full_image_name)
        if os.path.exists(small_image_path):
            continue
        full_image_path = os.path.join(_FULL_IMAGE_DIR_PATH, full_image_name)
        full_image = cv2.imread(full_image_path)

        isNextImage = False
        while default_pos is None:
            default_pos_tmp = (970, 70)
            default_size_tmp = (444, 232)
            right_bottom = (
                default_pos_tmp[0] + default_size_tmp[0], default_pos_tmp[1] + default_size_tmp[1])

            image = np.copy(full_image)
            cv2.rectangle(image, default_pos_tmp,
                          right_bottom, (255, 255, 255), 1)

            cv2.imshow('check image', image)
            key = cv2.waitKey(0)
            if key == ord('q'):
                exit()
            elif key == ord('n'):
                isNextImage = True
                break
            elif key == ord('s'):
                cv2.destroyAllWindows()
                default_pos = default_pos_tmp
                default_size = default_size_tmp
            else:
                continue

        if isNextImage:
            isNextImage = False
            continue

        # crop full image to small image
        right_bottom = (default_pos[0] + default_size[0],
                        default_pos[1] + default_size[1])
        small_image = full_image[default_pos[1]:right_bottom[1],
                                 default_pos[0]:right_bottom[0]]
        cv2.imwrite(small_image_path, small_image)
        os.remove(full_image_path)


if __name__ == '__main__':
    if not os.path.isdir(_IMAGE_OUTPUT_DIR_PATH):
        os.mkdir(_IMAGE_OUTPUT_DIR_PATH)
    if not os.path.isdir(_FULL_IMAGE_DIR_PATH):
        os.mkdir(_FULL_IMAGE_DIR_PATH)
    if not os.path.isdir(_SMALL_IMAGE_DIR_PATH):
        os.mkdir(_SMALL_IMAGE_DIR_PATH)
    if not os.path.isdir(_FINAL_IMAGE_DIR_PATH):
        os.mkdir(_FINAL_IMAGE_DIR_PATH)

    output_full_image()

    convert_full_image_to_small_image()

    print('done')
