import numpy as np
from toon.input.tsarray import TsArray


def test_creation():
    arr = TsArray([1, 2, 3], time=[1, 2, 3])
    # can make it
    assert(len(arr) == len(arr.time))
    nparr = np.array([1, 2, 3])
    # stores vals like numpy
    assert(all(nparr == arr))


def test_slice():
    arr = TsArray([[1, 2, 3], [4, 5, 6],
                   [7, 8, 9], [10, 11, 12]],
                  time=[0.1, 0.2, 0.3, 0.4])

    assert(all(arr[-1] == [10, 11, 12]))
    assert(arr[-1].time == 0.4)
    # non-scalar
    assert(all(arr[-2:].time == [0.3, 0.4]))
    # multidimensional slice (should take the first axis)
    assert(all(arr[-2:, :].time == [0.3, 0.4]))
    assert(all(arr[-2:].time == arr.time[-2:]))


def test_copy():
    arr = TsArray([[1, 2, 3], [4, 5, 6],
                   [7, 8, 9], [10, 11, 12]],
                  time=[0.1, 0.2, 0.3, 0.4])
    arr2 = arr.copy()
    assert(all(arr2.time == [0.1, 0.2, 0.3, 0.4]))
    # plug in an index (used to carry over to new objs)
    arr[1]
    arr2 = arr.copy()
    assert(all(arr2.time == [0.1, 0.2, 0.3, 0.4]))
