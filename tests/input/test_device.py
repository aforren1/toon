from pytest import raises
import numpy as np
from tests.input.mockdevices import Dummy, Timebomb, DummyList, SometimesNot, StructObs


def test_device_single():
    dev = Dummy()
    with dev:
        time, data = dev.read()
    assert(isinstance(time, float))
    assert(isinstance(data, np.ndarray))
    assert(data.shape == (5,))


def test_err():
    dev = Timebomb()
    with dev:
        with raises(ValueError):
            for i in range(12):
                dev.read()


def test_list():
    dev = DummyList()
    with dev:
        data = dev.read()

    assert(isinstance(data, list))
    assert(len(data) == 5)


def test_nones():
    dev = SometimesNot()
    data = []
    with dev:
        for i in range(10):
            data.append(dev.read())

    assert(data[1] is None)


def test_struct():
    dev = StructObs()
    with dev:
        time, data = dev.read()
    assert(data.ll.x == 0)
