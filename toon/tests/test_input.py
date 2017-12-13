from toon.input.mp_input import MultiprocessInput as MPI
from toon.input.mouse import Mouse
from toon.input.fake import FakeInput
from timeit import default_timer

dev = MPI(Mouse)
#dev = MPI(FakeInput, sampling_frequency=1000)

with dev as d:
    t0 = default_timer()
    t1 = t0 + 5
    t2 = 0
    while default_timer() < t1:
        time, data = d.read()
        if time is not None:
            print(time)
            #print(data)
        while default_timer() < t2:
            pass
        t2 = default_timer() + 0.016666

