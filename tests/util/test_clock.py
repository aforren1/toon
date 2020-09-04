from toon.util import MonoClock
from timeit import default_timer
import pickle as pkl


def test_clock():
    clk = MonoClock()
    assert(clk.get_time() > 0)
    assert(clk.getTime() > 0)
    t0 = clk.get_time()
    t1 = clk.get_time()
    print(t0, t1)
    assert (t1 > t0)
    t0 = clk.get_time_ns()
    t1 = clk.get_time_ns()
    assert (t1 > t0)

    clk2 = pkl.loads(pkl.dumps(clk))
    assert(clk2.dump_origin_ns() == clk.dump_origin_ns())
