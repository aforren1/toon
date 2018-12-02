from toon.input.device import BaseDevice, Obs
import ctypes
from pynput import mouse


class Mouse(BaseDevice):
    class Pos(Obs):
        shape = (2,)
        ctype = int

    class Clicks(Obs):
        shape = (1,)
        ctype = bool

    class Scroll(Obs):
        shape = (1,)
        ctype = ctypes.c_int

    sampling_frequency = 125

    def __init__(self, **kwargs):
        super(Mouse, self).__init__(**kwargs)

    def __enter__(self):
        self.dev = mouse.Listener(on_move=self.on_move,
                                  on_click=self.on_click,
                                  on_scroll=self.on_scroll)
        self.dev.start()
        self.dev.wait()
        self.x_prev = 0
        self.y_prev = 0
        self.data = []
        return self

    def read(self):
        if not self.data:
            return self.Returns()
        ret = self.data.copy()
        self.data = []
        return ret

    def on_move(self, x, y):
        # relative mouse position
        rets = self.Returns(pos=self.Pos(self.clock(), (x - self.x_prev,
                                                        y - self.y_prev)))
        self.x_prev = x
        self.y_prev = y
        self.data.append(rets)

    def on_click(self, x, y, button, pressed):
        rets = self.Returns(clicks=self.Clicks(self.clock(), pressed))
        self.data.append(rets)

    def on_scroll(self, x, y, dx, dy):
        rets = self.Returns(scroll=self.Scroll(self.clock(), dy))
        self.data.append(rets)

    def __exit__(self, *args):
        self.dev.stop()
        self.dev.join()


if __name__ == '__main__':
    import time
    from toon.input.mpdevice import MpDevice
    dev = MpDevice(Mouse)
    with dev:
        start = time.time()
        while time.time() - start < 10:
            dat = dev.read()
            if dat.any():
                print(dat)
            time.sleep(0.016)  # pretend to have a screen
