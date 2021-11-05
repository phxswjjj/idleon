import os
import time

import cv2
from fastai.vision.all import (ImageDataLoaders, cnn_learner, error_rate,
                               get_image_files, resnet18)

_RESOURCE_DIR_PATH = r'resources'
_RAW_DIR_PATH = os.path.join(_RESOURCE_DIR_PATH, r'dataset\raw')
_TEST_IMAGE_PATH = os.path.join(_RESOURCE_DIR_PATH, r'catch-test.png')

_IMAGE_OUTPUT_DIR_PATH = os.path.join(_RAW_DIR_PATH, r'lmb')
_FINAL_IMAGE_DIR_PATH = os.path.join(_IMAGE_OUTPUT_DIR_PATH, r'final')


def label_func(x): return x.parent.parent.name


def run():
    fnames = get_image_files(_FINAL_IMAGE_DIR_PATH)
    dls = ImageDataLoaders.from_path_func(
        _FINAL_IMAGE_DIR_PATH, fnames, label_func, bs=40, num_workers=0)
    learn = cnn_learner(dls, resnet18, metrics=error_rate)
    print('Loaded')

    learn.fine_tune(4, base_lr=1.0e-02)
    print('Fine tuned')

    learn.export()
    print('Exported')

    start_time = time.time()
    image = cv2.imread(_TEST_IMAGE_PATH)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    image = cv2.Canny(image, threshold1=100, threshold2=150)
    test = learn.predict(image)
    print("--- %s seconds ---" % (time.time() - start_time))
    print(test)


if __name__ == '__main__':
    run()
