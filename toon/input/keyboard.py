from toon.input.lsl_wrapper import BaseInput
from pynput import keyboard

class Keyboard(BaseInput):
    name = 'ToonKeyboard'
    type = 'Keyboard'
    channel_count = 2
    def __init__(self, keys=None, **kwargs):
        self._keys = keys
        super(Keyboard, self).__init__(channel_format='int32', **kwargs)
    def __enter__(self):
        super(Keyboard, self).__enter__()
        self._on = []
        self.dev = keyboard.Listener(on_press=self.on_press,
                                     on_release=self.on_release)
        self.dev.start()
        self.dev.wait()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dev.stop()
        self.dev.join()
    def on_press(self, key):
        ts = self.time()
        if not isinstance(key, keyboard.Key):
            if key.char in self._keys and key.char not in self._on:
                index = self._keys.index(key.char)
                self.outlet.push_sample([index, 1], ts)
                self._on.append(key.char)
    def on_release(self, key):
        ts = self.time()
        if not isinstance(key, keyboard.Key):
            if key.char in self._keys and key.char in self._on:
                index = self._keys.index(key.char)
                self.outlet.push_sample([index, 0], ts)
                self._on.remove(key.char)
