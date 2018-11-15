from toon.input.device import BaseDevice, Obs
import ctypes
from pynput import keyboard


class Keyboard(BaseDevice):
    class Key(Obs):
        shape = (1,)
        ctype = ctypes.c_char

    class Press(Obs):
        shape = (1,)
        ctype = ctypes.c_bool

    sampling_frequency = 100

    def __init__(self, keys=None, **kwargs):
        if keys is None:
            raise ValueError('Specify keys.')
        self.keys = keys
        super(Keyboard, self).__init__(**kwargs)

    def __enter__(self):
        self.dev = keyboard.Listener(on_press=self.on_press,
                                     on_release=self.on_release)
        self.data = []
        self._on = []
        self.dev.start()
        self.dev.wait()
        return self

    def read(self):
        if not self.data:
            return self.Returns()
        ret = self.data.copy()
        self.data = []
        return ret

    def on_press(self, key):
        time = self.clock()
        if not isinstance(key, keyboard.Key):
            # check if key is of interest, and
            # ignore repeating keys
            if key.char in self.keys and key.char not in self._on:
                rets = self.Returns(key=self.Key(time, key.char),
                                    press=self.Press(time, True))
                self.data.append(rets)
                self._on.append(key.char)

    def on_release(self, key):
        time = self.clock()
        if not isinstance(key, keyboard.Key):
            if key.char in self.keys and key.char in self._on:
                rets = self.Returns(key=self.Key(time, key.char),
                                    press=self.Press(time, False))
                self.data.append(rets)
                self._on.remove(key.char)

    def __exit__(self, *args):
        self.dev.stop()
        self.dev.join()


if __name__ == '__main__':
    import time
    from toon.input.mpdevice import MpDevice
    dev = MpDevice(Keyboard, keys=['a', 's', 'd', 'f'])
    with dev:
        start = time.time()
        while time.time() - start < 10:
            dat = dev.read()
            if dat.any():
                print(dat)
            time.sleep(0.016)
