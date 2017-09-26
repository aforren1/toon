import numpy as np
import keyboard as kb
from toon.input.base_input import DummyTime


class Keyboard(object):
    def __init__(self,
                 clock_source=DummyTime,
                 keys=None):

        if keys is None:
            raise ValueError('`keys` must be a list of keys of interest.')

        self.time = clock_source
        self._lenkeys = len(keys)
        self._keys = keys
        self._buffer = np.full(self._lenkeys, 0)
        self._outbuffer = np.full(self._lenkeys, 0)

    def __enter__(self):
        self._start_time = self.time.getTime()
        self._buffer[:] = 0
        self._outbuffer[:] = 0
        n = 0
        for key in self._keys:
            kb.add_hotkey(key, self._add_array, (n,),
                          timeout=0.001)
            kb.add_hotkey(key, self._rem_array, (n,),
                          timeout=0.001,
                          trigger_on_release=True)
            n += 1
        return self

    def __exit__(self, type, value, traceback):
        kb.clear_all_hotkeys()

    def read(self):
        timestamp = self.time.getTime()
        np.copyto(self._outbuffer, self._buffer)
        return self._outbuffer, timestamp

    def _add_array(self, index):
        self._buffer[index] = 1

    def _rem_array(self, index):
        self._buffer[index] = 0
