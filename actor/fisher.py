import os
from enum import Enum, unique

import cv2

if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.realpath('.'))
from utility.stopwatch import StopWatch


@unique
class DetectResultType(Enum):
    NG = 0
    OK = 1
    WAIT = 2


class Actor:
    def __init__(self, template, threshold=0.8):
        self.template = template
        self.threshold = threshold
        self.last_source = None

    def detect(self, source) -> (DetectResultType, (int, int)):
        result = DetectResultType.WAIT
        loc = (None, None)
        template = self.template
        threshold = self.threshold
        self.last_source = source

        matchResult = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(matchResult)
        if max_val >= threshold:
            result = DetectResultType.OK
            loc = max_loc
        else:
            result = DetectResultType.NG

        return (result, loc)

    def detect_until(self, fetch, timeout=3) -> (DetectResultType, (int, int)):
        result = DetectResultType.WAIT
        loc = (None, None)
        template = self.template
        threshold = self.threshold

        sw = StopWatch()
        sw.start()

        execute_time = 0
        while execute_time < 1 or sw.elapsed_sec() < timeout:
            execute_time += 1
            source = fetch()
            r, l = self.detect(source)
            if r == DetectResultType.OK:
                result = r
                loc = l
                break

        if result == DetectResultType.WAIT:
            result = DetectResultType.NG
        return (result, loc)


if __name__ == '__main__':
    _RESOURCE_DIR_PATH = r'resources'
    _FISHBALL_DIR_PATH = os.path.join(_RESOURCE_DIR_PATH, 'fish-ball')
    img = cv2.imread(os.path.join(
        _RESOURCE_DIR_PATH, 'fish-ball.jpg'), 0)
    actor = Actor(template=img)

    def fetch():
        return cv2.imread(os.path.join(
            _RESOURCE_DIR_PATH, 'tmp4.jpg'), 0)

    result, loc = actor.detect_until(fetch=fetch)
    print(result, loc)
    if result == DetectResultType.OK:
        h, w = img.shape
        source = actor.last_source
        cv2.rectangle(source, loc, (loc[0] + w, loc[1] + h),
                      (255, 255, 255), 1)
        cv2.imshow('view', source)
        cv2.waitKey(0)
