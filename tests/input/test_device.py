from tests.input.mockdevices import Dummy, DummyList
from toon.input.device import Obs


def test_device_single():
    dev = Dummy()
    res = dev.read()
    assert(issubclass(type(res[0]), Obs))
    assert(issubclass(type(res.num1.time), float))
    assert(len(res.num1.data) == 5)


def test_device_multi():
    dev = DummyList()
    res = dev.read()
    assert(len(res) == 2)


def test_context():
    dev = Dummy()
    with dev:
        res = dev.read()
    assert(issubclass(type(res[0]), Obs))
    assert(issubclass(type(res.num1.time), float))
    assert(len(res.num1.data) == 5)
