import time

from actor import streamer

if __name__ == '__main__':
    app = streamer.create(target_win_title='Legends Of Idleon')
    app.show()
    print('done')
