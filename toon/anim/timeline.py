
# clock_fun should be time.perf_counter, time.monotonic,
# timeit.default_timer (for best compatibility)

# start should be attached to win.callOnFlip()
# next_frame should be attached to win.callOnFlip()
from timeit import default_timer


class Timeline(object):
    def __init__(self, clock_fun=default_timer):
        self.clock_fun = clock_fun
        self.running = False

    def start(self):
        self.running = True
        self.start_time = self.clock_fun()
        self.prev_frame_time = self.start_time
        self.prev_frame_dur = 0

    def stop(self):
        self.running = False
        self.start_time = self.clock_fun()
        self.prev_frame_time = self.start_time
        self.prev_frame_dur = 0

    def next_frame(self):
        # should be run by win.callOnFlip
        now = self.clock_fun()
        if not self.running:
            return
        self.prev_frame_dur = now - self.prev_frame_time
        self.prev_frame_time = now

    @property
    def frame_time(self):
        return self.prev_frame_time - self.start_time
