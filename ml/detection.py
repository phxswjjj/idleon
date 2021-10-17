
import os

import cv2
import numpy as np

_RESOURCE_DIR_PATH = r'resources'

if __name__ == '__main__':

    img_full = cv2.imread(os.path.join(_RESOURCE_DIR_PATH, 'tmp.jpg'), 0)

    img_coin = cv2.imread(os.path.join(
        _RESOURCE_DIR_PATH, 'Copper_Coin.png'), 0)

    res = cv2.matchTemplate(img_full, img_coin, cv2.TM_CCOEFF_NORMED)

    threshold = 0.8
    h, w = img_coin.shape

    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img_full, pt, (pt[0] + w, pt[1] + h), (255, 255, 255), 1)

    cv2.namedWindow("show", cv2.WINDOW_NORMAL)
    cv2.imshow('show', img_full)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
