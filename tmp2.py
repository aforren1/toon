# What we want:
#
# If sampling a local device, spawn another process (via multiprocessing), and spin on that
# If sampling a remote device, assume that it exists already and start reading from it
# Have a standalone device class (minus LSL stuff)
import time
import multiprocessing as mp
from pylsl import (StreamInfo, StreamOutlet, StreamInlet,
                   resolve_stream, local_clock, IRREGULAR_RATE)
import numpy as np
import matplotlib.pyplot as plt
from psychopy import clock

clk = clock.monotonicClock
class Test(object):
    def __init__(self):
        self.name = type(self).__name__
        self.outlet = None
    def __enter__(self):
        from pynput import mouse
        self.info = StreamInfo('???', 'Mouse', 2, IRREGULAR_RATE, 'int32')
        self.outlet = StreamOutlet(self.info)
        self.dev = mouse.Listener(on_move=self.on_move)
        self.dev.start()
        self.dev.wait()
        return self
    def __exit__(self, a, b, c):
        self.dev.stop()
        self.dev.join()
    def on_move(self, x, y):
        #ts = local_clock()
        ts = clk.getTime()
        self.outlet.push_sample([x, y], ts)

def _worker(flag, remote_ready):
    dev = Test()
    remote_ready.set()
    with dev:
        while not flag.is_set():
            pass

if __name__ == '__main__':
    flag = mp.Event()
    remote_ready = mp.Event()
    proc = mp.Process(target=_worker, args=(flag, remote_ready))
    proc.daemon = True
    proc.start()
    remote_ready.wait()
    streams = resolve_stream('type', 'Mouse')
    inlet = StreamInlet(streams[0])
    t0 = time.time()
    t1 = t0 + 10
    times = []
    while time.time() < t1:
        chunk, timestamps = inlet.pull_chunk()
        if timestamps:
            print(chunk)
            print(timestamps)
            times.extend(timestamps)
    inlet.close_stream()
    flag.set()
    plt.plot(np.diff(times))
    plt.show()


