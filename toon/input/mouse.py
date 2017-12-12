from ctypes import c_int32
from toon.input.mp_input import BaseInput
from pynput import mouse

class Mouse(BaseInput):
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 100)
    def data_shapes(**kwargs):
        return [[2]]
    def data_types(**kwargs):
        return [c_int32]
    def __init__(self, sampling_frequency=100, **kwargs):
        super(Mouse, self).__init__(sampling_frequency=sampling_frequency, **kwargs)
    def __enter__(self):
        self.dev = mouse.Listener(on_move=self.on_move)
        self.dev.start()
        self.dev.wait()
        self.times = []
        self.readings = []
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dev.stop()
        self.dev.join()
    def on_move(self, x, y):
        self.times.append(self.clock())
        self.readings.append([x, y])
    def read(self):
        read2 = []
        read2[:] = self.readings
        self.readings = []
        return read2
