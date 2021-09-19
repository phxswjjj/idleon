from actor import streamer
import time

if __name__ == '__main__':
    app = streamer.create()
    app.show()
    print('done')
