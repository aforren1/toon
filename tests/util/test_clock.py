from toon.util import MonoClock
from timeit import default_timer


def test_clock():
    clk = MonoClock()
    assert(clk.get_time() > 0)
    assert(clk.getTime() > 0)
