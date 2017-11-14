from toon.input.lsl_wrapper import BaseInput
from pynput import mouse


class Mouse(BaseInput):
    name = 'ToonMouse'
    type = 'Mouse'
    channel_count = 2

    def __init__(self, **kwargs):
        super(Mouse, self).__init__(channel_format='int32', **kwargs)
    def __enter__(self):
        super(Mouse, self).__enter__()
        self.dev = mouse.Listener(on_move=self.on_move)
        self.dev.start()
        self.dev.wait()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dev.stop()
        self.dev.join()
    def on_move(self, x, y):
        ts = self.time()
        self.outlet.push_sample([x, y], ts)
    def read(self):
        pass

