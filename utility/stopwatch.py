from time import sleep
from datetime import datetime, timedelta
import math


class StopWatch():
    def __init__(self):
        self.fromInstance: datetime = None
        self.toInstance: datetime = None
        self._framesCount: int = 0

    def start(self) -> datetime:
        self.fromInstance = datetime.now()
        self.toInstance = None
        self._framesCount = 0
        return self.fromInstance

    def stop(self) -> datetime:
        self.toInstance = datetime.now()
        return self.toInstance

    def elapsed_sec(self) -> float:
        dif = self.elapsed()
        return dif.total_seconds()

    def elapsed(self) -> timedelta:
        t1 = self.fromInstance
        t2 = self.toInstance if self.toInstance else datetime.now()
        return t2 - t1

    def fps(self, framesCount: int = None) -> int:
        sec = self.elapsed_sec()
        if framesCount:
            self._framesCount = framesCount
        else:
            self._framesCount += 1
        return math.trunc(self._framesCount/sec)


if __name__ == '__main__':
    sw = StopWatch()
    sw.start()
    max_times = 3
    for i in range(max_times):
        sleep(1)
        print('Elapsed sec:', sw.elapsed_sec(), 'fps:', sw.fps((i + 1) * 10))
    sw.stop()

    sleep(1)
    print('Final Elapsed sec:', sw.elapsed_sec(),
          'fps:', sw.fps(max_times * 10))
