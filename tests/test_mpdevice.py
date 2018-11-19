from time import sleep
import numpy as np
from toon.input.mpdevice import MpDevice
from tests.mockdevices import Dummy, DummyList

# bump up the sampling frequency for tests
Dummy.sampling_frequency = 1000
DummyList.sampling_frequency = 1000


def test_device_single():
    # single device with two data sources
    dev = MpDevice(Dummy)
    dev.start()
    sleep(0.2)
    res = dev.read()
    dev.stop()
    assert(len(res.num1.time) > 5)
    assert(len(res.num1.time) == res.num1.data.shape[0])
    assert(res.num1.data.shape[1] == 5)
    assert(res.num2.data.dtype == np.int32)


def test_device_list():
    # two observations per read on the device
    dev = MpDevice(DummyList)
    dev.start()
    sleep(0.2)
    res = dev.read()
    dev.stop()
    assert(len(res.num1.time) > 5)
    assert(len(res.num1.time) == res.num1.data.shape[0])
    assert(res.num1.data.shape[1] == 5)
    assert(res.num2.data.dtype == np.int32)
    assert(res.num1.data.shape[0] > res.num2.data.shape[1])


def test_restart():
    # start & stop device
    dev = MpDevice(Dummy)
    dev.start()
    sleep(0.2)
    res = dev.read()
    dev.stop()
    dev.start()
    sleep(0.2)
    res2 = dev.read()
    dev.stop()
    assert(abs(len(res2.num1.time) - len(res.num1.time)) < 5)


def test_context():
    # device as context manager
    dev = MpDevice(Dummy)
    with dev:
        sleep(0.2)
        res = dev.read()
    assert(len(res.num1.time) > 5)
    assert(len(res.num1.time) == res.num1.data.shape[0])
    assert(res.num1.data.shape[1] == 5)
    assert(res.num2.data.dtype == np.int32)


def test_multi_devs():
    # 2+ devices at once (each gets own process)
    dev1 = MpDevice(Dummy)
    dev2 = MpDevice(Dummy)
    with dev1, dev2:
        sleep(0.1)
        res1 = dev1.read()
        res2 = dev2.read()

    assert(res1.num1.time is not None)
    assert(res2.num1.time is not None)


def test_slow():
    # sluggish devices
    Dummy.sampling_frequency = 0.1
    dev = MpDevice(Dummy)
    with dev:
        sleep(0.15)
        res = dev.read()

    Dummy.sampling_frequency = 1000
    # might get one reading out of the fast data...
    assert(res.num1.time is not None)
