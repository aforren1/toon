from toon.util import MonoClock
from timeit import default_timer


def test_clock():
    clk = MonoClock()
    assert(clk.get_time() > 0)
    assert(clk.getTime() > 0)
    t0 = clk.get_time()
    t1 = clk.get_time()
    print(t0, t1)
    assert(t1 > t0)
