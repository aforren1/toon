import numpy as np
from toon.input.base_input import BaseInput

class Keyboard(BaseInput):
    def __init__(self, keys=None, **kwargs):
        """
        Args:
            keys (list): List of keys of interest, e.g. ['a', 's', 'd', 'f']

        Notes:
            Returns a *change* in state (1 for press, -1 for release).
                However, there's a bug somewhere that when you release one key while holding
                others down, it'll count as a release on *all* keys (only checked on Windows).
        """
        self._keys = keys
        if not isinstance(self._keys, list):
            raise ValueError('`keys` must be a list of keys of interest.')
        BaseInput.__init__(self, **kwargs)
        self._buffer = np.full(len(self._keys), 0)
        self._state = np.copy(self._buffer)
        self._temp_time = None
        self._data_buffer = np.full(len(self._keys), np.nan)

    def __enter__(self):
        import keyboard
        self._device = keyboard
        self._buffer[:] = 0
        n = 0
        for key in self._keys:
            keyboard.add_hotkey(key, self._add_array, (n,), timeout=0)
            keyboard.add_hotkey(key, self._rem_array, (n,), timeout=0, trigger_on_release=True)
            n += 1
        return self

    def read(self):
        if self._buffer.any():
            np.copyto(self._data_buffer, self._buffer)
            self._buffer.fill(0)
            return {'time': self._temp_time, 'data': self._data_buffer}
        return None

    def __exit__(self, type, value, traceback):
        self._device.clear_all_hotkeys()

    def _add_array(self, index):
        """Only get onset, not bouncing"""
        self._temp_time = self.time()
        if self._state[index] == 0.0:
            self._buffer[index] = 1
            self._state[index] = 1
        else:
            self._buffer[index] = 0

    def _rem_array(self, index):
        self._temp_time = self.time()
        self._buffer[index] = -1
        self._state[index] = 0
