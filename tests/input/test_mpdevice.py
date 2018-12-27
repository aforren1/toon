from time import sleep

import numpy as np
from pytest import approx, raises
from tests.input.mockdevices import Dummy, DummyList, SingleResp, Timebomb

from toon.input.clock import mono_clock
from toon.input.mpdevice import MpDevice

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
    assert(len(res.num1.time) == res.num1.shape[0])
    assert(res.num1.shape[1] == 5)
    assert(res.num2.dtype == np.int32)


def test_single_resp():
    dev = MpDevice(SingleResp)
    dev.start()
    sleep(0.2)
    res = dev.read()
    dev.stop()
    assert(isinstance(res, np.ndarray))
    assert(type(res.time) is np.ndarray)


def test_ringbuffer():
    original_fs = SingleResp.sampling_frequency
    SingleResp.sampling_frequency = 10
    dev = MpDevice(SingleResp)
    with dev:
        sleep(5)
        res = dev.read()
    assert(all(np.diff(res) == 1))
    assert(all(np.diff(res.time) > 0))
    SingleResp.sampling_frequency = original_fs


def test_have_all_data():
    dev = MpDevice(SingleResp)
    datae = []
    times = []
    with dev:
        for i in range(100):
            sleep(0.2)
            data = dev.read()
            if data is not None:
                datae.append(np.copy(data))
                times.append(np.copy(data.time))
    times = np.hstack(times)
    datae = np.hstack(datae)
    # check time is always increasing
    assert((np.diff(times) > 0).all())
    # check data (should be monotonically increasing)
    assert((np.diff(datae) == 1).all())


def test_device_list():
    # two observations per read on the device
    dev = MpDevice(DummyList)
    dev.start()
    sleep(0.2)
    res = dev.read()
    dev.stop()
    assert(len(res.num1.time) > 5)
    assert(len(res.num1.time) == res.num1.shape[0])
    assert(res.num1.shape[1] == 5)
    assert(res.num2.dtype == np.int32)
    assert(res.num1.shape[0] > res.num2.shape[1])


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
    assert(res.any() and res2.any())


def test_context():
    # device as context manager
    dev = MpDevice(Dummy)
    with dev:
        sleep(0.2)
        res = dev.read()
    assert(len(res.num1.time) > 5)
    assert(len(res.num1.time) == res.num1.shape[0])
    assert(res.num1.shape[1] == 5)
    assert(res.num2.dtype == np.int32)


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


def test_remote_clock():
    # does the clock origin match?
    # the most recent reading should've been within
    # one sampling period
    dev = MpDevice(SingleResp, clock=mono_clock.getTime)
    sleep(0.5)
    with dev:
        sleep(0.1)
        res = dev.read()
        time = mono_clock.get_time()
    assert(time - res.time[-1] == approx(1.0/SingleResp.sampling_frequency, abs=1e-3))


def test_already_closed():
    dev = MpDevice(SingleResp)
    dev.start()
    res = dev.read()
    dev.stop()
    with raises(ValueError):
        dev.read()


def test_catch_remote_err():
    dev = MpDevice(Timebomb)
    with dev:
        sleep(0.1)
        with raises(ValueError):
            res = dev.read()
