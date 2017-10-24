from toon.input.base_input import BaseInput
from pynput import keyboard

class Keyboard(BaseInput):
    def __init__(self, keys=None, **kwargs):
        """

        Args:
            keys: (list): List of keys of interest, e.g. ['a', 's', 'd', 'f'].
            **kwargs: Passed to :class:BaseInput.

        Notes:
            Read function returns only the press, not the release (for now).
            Both the character and the index (position in the list provided) are
            returned in the dict, as well as the type of event (press vs. release).
        """

        self._keys = keys
        if not isinstance(self._keys, list):
            raise ValueError('`keys` must be a list of keys of interest.')
        BaseInput.__init__(self, **kwargs)
        self._events = list()
        self._on = list()

    def __enter__(self):
        self._device = keyboard.Listener(on_press=self._on_press,
                                         on_release=self._on_release)
        self._device.start()
        self._device.wait()
        return self

    def read(self):
        send_data = self._events[:]
        self._events.clear()
        if send_data:
            return send_data[0]  # only return first press (to fix later)
        return None

    def __exit__(self, type, value, traceback):
        self._device.stop()
        self._device.join()

    def _on_press(self, key):
        time = self.time()
        if not isinstance(key, keyboard.Key):
            if key.char in self._keys and key.char not in self._on:
                index = self._keys.index(key.char)
                data = {'time': time, 'index': index, 'char': key.char, 'type': 'press'}
                self._events.append(data)
                self._on.append(key.char)

    def _on_release(self, key):
        time = self.time()
        if not isinstance(key, keyboard.Key):
            if key.char in self._keys and key.char in self._on:
                index = self._keys.index(key.char)
                data = {'time': time, 'index': index, 'char': key.char, 'type': 'release'}
                self._events.append(data)
                self._on.remove(key.char)
