from device import BaseDevice, Obs
import ctypes
from pynput import mouse


class Mouse(BaseDevice):
    class Pos(Obs):
        shape = (2,)
        ctype = ctypes.c_uint

    class Clicks(Obs):
        shape = (1,)
        ctype = ctypes.c_uint

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

    def read(self):
        if not self.data:
            return self.Returns()
        ret = self.data.copy()
        self.data = []
        return ret

    def on_move(self, x, y):
        # relative mouse position
        print((x, y))
        rets = self.Returns(pos=self.Pos(self.clock(), (x - self.x_prev,
                                                        y - self.y_prev)))
        self.data.append(rets)

    def on_click(self, x, y, button, pressed):
        rets = self.Returns(clicks=self.Clicks(self.clock(), button.value))
        self.data.append(rets)

    def on_scroll(self, x, y, dx, dy):
        rets = self.Returns(self.Scroll(self.clock(), dy))
        self.data.append(rets)

    def __exit__(self, *args):
        self.dev.stop()
        self.dev.join()


if __name__ == '__main__':
    # from time import time

    # dev = Mouse()
    # with dev:
    #     start = time()
    #     while time() - start < 10:
    #         dat = dev.read()
    #         if dat:
    #             print(dat)
    import time
    from toon.input.mpdevice import MpDevice
    dev = MpDevice(Mouse)
    with dev:
        start = time.time()
        while time.time() - start < 10:
            dat = dev.read()
            if any([x.time is not None for x in dat]):
                print(dat)
