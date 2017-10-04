import numpy as np
from toon.input.base_input import BaseInput, DummyTime

class Keyboard(BaseInput):
    def __init__(self,
                 clock_source=DummyTime,
                 keys=None,
                 multiprocess=False,
                 nrow=10):
        if keys is None or not isinstance(keys, list):
            raise ValueError('`keys` must be a list of keys of interest.')
        BaseInput.__init__(self, clock_source, multiprocess, (nrow, len(keys)))
        self._lenkeys = len(keys)
        self._keys = keys
        self._buffer = np.full(self._lenkeys, 0)
        self._outbuffer = np.copy(self._buffer)
        self._state = np.copy(self._buffer)
        self._temptime = None

    def _init_device(self):
        import keyboard
        self._device = keyboard
        self._buffer[:] = 0
        n = 0
        for key in self._keys:
            keyboard.add_hotkey(key, self._add_array, (n,), timeout=0)
            keyboard.add_hotkey(key, self._rem_array, (n,), timeout=0, trigger_on_release=True)
            n += 1

    def _add_array(self, index):
        """Only get onset, not bouncing"""
        self._temptime = self.time.getTime()
        if self._state[index] == 0.0:
            self._buffer[index] = 1
            self._state[index] = 1
        else:
            self._buffer[index] = 0

    def _rem_array(self, index):
        self._temptime = self.time.getTime()
        self._buffer[index] = -1
        self._state[index] = 0

    def _read(self):
        if self._buffer.any():
            np.copyto(self._outbuffer, self._buffer)
            self._buffer.fill(0)
            return self._temptime, self._outbuffer
        return None, None

    def _stop_device(self):
        self._device.clear_all_hotkeys()

    def _close_device(self):
        pass

class DebugKeyboard(BaseInput):
    def __init__(self,
                 clock_source=DummyTime,
                 keys=None,
                 multiprocess=False,
                 nrow=10):
        if keys is None or not isinstance(keys, list):
            raise ValueError('`keys` must be a list of keys of interest.')

        BaseInput.__init__(self, clock_source, multiprocess, (nrow, len(keys)))
        self._lenkeys = len(keys)
        self._keys = keys
        self._buffer = np.full(self._lenkeys, 0)
        self._sampling_period = 0.01

    def _init_device(self):
        import keyboard
        self._device = keyboard
        self._buffer[:] = 0
        n = 0
        for key in self._keys:
            keyboard.add_hotkey(key, self._add_array, (n,), timeout=0)
            keyboard.add_hotkey(key, self._rem_array, (n,), timeout = 0, trigger_on_release=True)
            n += 1


    def _read(self):
        return self.time.getTime(), self._buffer

    def _stop_device(self):
        self._device.clear_all_hotkeys()

    def _close_device(self):
        pass

    def _add_array(self, index):
        self._buffer[index] = 1

    def _rem_array(self, index):
        self._buffer[index] = 0
