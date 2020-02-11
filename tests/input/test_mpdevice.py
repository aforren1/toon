from time import sleep
from pytest import raises, approx
import numpy as np
from tests.input.mockdevices import (Dummy, Timebomb, DummyList,
                                     SometimesNot, StructObs, Incrementing,
                                     NoData)
from toon.util import mono_clock
from toon.input import MpDevice

Dummy.sampling_frequency = 1000


def test_device_single():
    dev = MpDevice(Dummy())
    dev.start()
    sleep(0.25)
    res = dev.read()
    dev.stop()
    assert(res is not None)
    time, data = res
    print(np.diff(time))
    print(data.shape)
    assert(data.shape[0] > 10)
    assert(data.shape[0] == time.shape[0])


def test_err():
    dev = MpDevice(Timebomb())
    with dev:
        sleep(0.2)
        with raises(ValueError):
            dat = dev.read()


def test_list():
    dev = MpDevice(DummyList())
    with dev:
        sleep(0.2)
        time, data = dev.read()
    assert(data.shape[0] > 10)
    assert(data.shape[0] == time.shape[0])


def test_nones():
    dev = MpDevice(SometimesNot())
    with dev:
        sleep(0.2)
        time, data = dev.read()
    print(data.shape)
    assert(data.shape[0] > 10)
    assert(data.shape[0] == time.shape[0])


def test_struct():
    dev = MpDevice(StructObs())
    with dev:
        sleep(0.2)
        time, data = dev.read()
    assert(data.shape[0] > 10)
    assert(data.shape[0] == time.shape[0])


def test_freq():
    original_fs = Dummy.sampling_frequency
    Dummy.sampling_frequency = 1

    dev = MpDevice(Dummy())
    with dev:
        sleep(4)
        time, val = dev.read()

    assert(time.shape[0] == 1)
    assert(val.shape == (1, 5))
    print(time, val)
    Dummy.sampling_frequency = original_fs


def test_ringbuffer():
    dev = MpDevice(Dummy(), buffer_len=1)
    with dev:
        sleep(1)
        time, val = dev.read()

    assert(time.shape[0] == 1)
    assert(val.shape == (1, 5))
    print(time, val)


def test_mono():
    dev = MpDevice(Incrementing(), buffer_len=10)
    with dev:
        sleep(1)
        time, val = dev.read()

    print(time, val)
    assert(all(np.diff(time) > 0))
    assert(all(np.diff(val) > 0))


def test_read_multi():
    dev = MpDevice(Incrementing())
    with dev:
        times, dats = [], []
        for i in range(500):
            data = dev.read()
            if data:
                times.append(data.time)
                dats.append(data.data)
            sleep(0.016)
    times = np.hstack(times)
    vals = np.hstack(dats)
    print(times)
    print(vals)
    assert(all(np.diff(times)) > 0)
    assert(all(np.diff(vals)) > 0)


def test_restart():
    dev = MpDevice(Dummy())
    with dev:
        sleep(0.2)
        res = dev.read()
    with dev:
        sleep(0.2)
        res2 = dev.read()
    print(res[0])
    print(res2[0])
    assert(res[0].any() and res2[0].any())
    assert(res[0][-1] < res2[0][0])


def test_multi_devs():
    dev1 = MpDevice(Dummy())
    dev2 = MpDevice(Dummy())

    with dev1, dev2:
        sleep(0.2)
        time1, data1 = dev1.read()
        time2, data2 = dev2.read()

    print(time1[-5:], time2[-5:])


def test_none():
    dev = MpDevice(NoData())
    with dev:
        sleep(0.2)
        res = dev.read()

    assert(res is None)


def test_remote_clock():
    dev = MpDevice(Dummy(clock=mono_clock.get_time))
    sleep(0.5)
    with dev:
        sleep(0.1)
        time, data = dev.read()
        tmp = mono_clock.get_time()
    print(tmp - time[-1])
    assert(tmp - time[-1] == approx(1.0/Dummy.sampling_frequency, abs=3e-3))


def test_already_closed():
    dev = MpDevice(Dummy())
    dev.start()
    res = dev.read()
    dev.stop()
    with raises(ValueError):
        dev.read()


def test_no_local():
    local_dev = Dummy()
    dev = MpDevice(local_dev)
    with dev:
        with raises(ValueError):
            with local_dev:
                res = local_dev.read()
