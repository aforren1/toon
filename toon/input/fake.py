import numpy as np
from toon.input.lsl_wrapper import BaseInput

class FakeInput(BaseInput):
    name = 'FakeInput'
    type = 'FakeInput'
    channel_count = 10

    def __init__(self, period=0.001, **kwargs):
        super(FakeInput, self).__init__(**kwargs)
        self.period = period
    def __enter__(self):
        super(FakeInput, self).__enter__()
        self.t1 = self.time()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def read(self):
        data = np.random.random(self.channel_count)
        ts = self.time()
        self.outlet.push_sample(data, ts)
        while self.time() < self.t1:
            pass
        self.t1 = self.time() + self.period

