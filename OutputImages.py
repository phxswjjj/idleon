import os
from datetime import datetime

import cv2
import numpy as np

_RESOURCE_DIR_PATH = r'resources'
_RAW_DIR_PATH = os.path.join(_RESOURCE_DIR_PATH, r'dataset\raw')
_FULL_DIR_PATH = os.path.join(_RESOURCE_DIR_PATH, r'dataset\full')
_SMALL_DIR_PATH = os.path.join(_RESOURCE_DIR_PATH, r'dataset\small')
_FINAL_DIR_PATH = os.path.join(_RESOURCE_DIR_PATH, r'dataset\final')

_IMAGES_RAWDATA_PATH = os.path.join(_RAW_DIR_PATH, 'images.npy')
_LABELS_RAWDATA_PATH = os.path.join(_RAW_DIR_PATH, 'labels.npy')


def output_full_image():
    if not os.path.exists(_IMAGES_RAWDATA_PATH) \
            or not os.path.exists(_LABELS_RAWDATA_PATH):
        return

    images = np.load(_IMAGES_RAWDATA_PATH, allow_pickle=True)[1:-10]
    labels = np.load(_LABELS_RAWDATA_PATH, allow_pickle=True)[1:-10]
    print(f'raw images count: {len(images)}')

    batch_id = (datetime.now() - datetime(2021, 10, 10)).total_seconds()
    for i, image in enumerate(images):
        label = labels[i]
        label_dir_path = os.path.join(_FULL_DIR_PATH, label)
        if not os.path.isdir(label_dir_path):
            os.makedirs(label_dir_path)
        full_image_path = os.path.join(
            label_dir_path, f'{batch_id}_{i}.png')
        cv2.imwrite(full_image_path, image)

    os.remove(_IMAGES_RAWDATA_PATH)
    os.remove(_LABELS_RAWDATA_PATH)


def convert_full_image_to_small_image():
    label_names = os.listdir(_FULL_DIR_PATH)

    for label_name in label_names:
        label_dir_path = os.path.join(_FULL_DIR_PATH, label_name)
        image_names = os.listdir(label_dir_path)

        default_pos = None
        default_size = None

        for image_name in image_names:
            full_image_path = os.path.join(label_dir_path, image_name)
            small_dir_path = os.path.join(_SMALL_DIR_PATH, label_name)
            if not os.path.isdir(small_dir_path):
                os.makedirs(small_dir_path)
            small_image_path = os.path.join(
                small_dir_path, image_name)
            if os.path.exists(small_image_path):
                continue
            full_image = cv2.imread(full_image_path)

            isNextImage = False
            while default_pos is None:
                default_pos_tmp = (970, 50)
                default_size_tmp = (444, 252)
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


def convert_small_image_to_final_image():
    label_names = os.listdir(_SMALL_DIR_PATH)

    for label_name in label_names:
        label_dir_path = os.path.join(_SMALL_DIR_PATH, label_name)
        image_names = os.listdir(label_dir_path)

        for image_name in image_names:
            small_image_path = os.path.join(label_dir_path, image_name)
            final_dir_path = os.path.join(_FINAL_DIR_PATH, label_name)
            if not os.path.isdir(final_dir_path):
                os.makedirs(final_dir_path)
            final_image_path = os.path.join(
                final_dir_path, image_name)
            if os.path.exists(final_image_path):
                continue
            small_image = cv2.imread(small_image_path)

            final_image = cv2.cvtColor(small_image, cv2.COLOR_RGB2GRAY)
            final_image = cv2.GaussianBlur(final_image, (5, 5), 0)
            final_image = cv2.Canny(
                final_image, threshold1=100, threshold2=150)
            cv2.imwrite(final_image_path, final_image)


if __name__ == '__main__':
    if not os.path.isdir(_FULL_DIR_PATH):
        os.mkdir(_FULL_DIR_PATH)
    if not os.path.isdir(_SMALL_DIR_PATH):
        os.mkdir(_SMALL_DIR_PATH)
    if not os.path.isdir(_FINAL_DIR_PATH):
        os.mkdir(_FINAL_DIR_PATH)

    output_full_image()

    convert_full_image_to_small_image()

    convert_small_image_to_final_image()

    print('done')
