import ctypes
from time import sleep
import numpy as np
from unittest import TestCase
from toon.input.fake import FakeInput
from toon.input import MultiprocessInput as MpI
from tests.mock_devices import HetInput


class TestFake(TestCase):
    def test_dev_instantiation(self):
        dev = FakeInput(sampling_frequency=100)
        with dev as d:
            time, dat = d.read()
        self.assertEqual(len(dat), 5)
        self.assertTrue(isinstance(time, float))

    def test_multi_data(self):
        dev = FakeInput(sampling_frequency=10, data_shape=[
                        [5], [3, 2]], data_type=[ctypes.c_double]*2)
        with dev as d:
            sleep(0.5)
            time, data = d.read()
        self.assertTrue(isinstance(data, list))
        self.assertEqual(data[0].shape, (5,))
        self.assertEqual(data[1].shape, (3, 2))


class TestMpInput(TestCase):
    def test_single_data(self):
        dev = MpI(FakeInput)
        dev.start()
        sleep(0.5)
        time, data = dev.read()
        dev.stop()
        self.assertEqual(type(time), np.ndarray)

    def test_multi_data(self):
        dev = MpI(FakeInput, data_type=[
                  ctypes.c_double]*2, data_shape=[[5], [3]])
        dev.start()
        sleep(0.5)
        time, data = dev.read()
        dev.stop()
        self.assertEqual(data[0].shape[1:], (5,))
        self.assertEqual(data[1].shape[1:], (3,))

    def test_nd_data(self):
        dev = MpI(FakeInput, data_shape=[[5, 4, 3, 2, 1]])
        dev.start()
        sleep(0.5)
        time, data = dev.read()
        dev.stop()
        self.assertEqual(data.shape[1:], (5, 4, 3, 2, 1))

    def test_high_freq(self):
        dev = MpI(FakeInput, sampling_frequency=10000)
        dev.start()
        sleep(0.5)
        time, data = dev.read()
        print(time)
        dev.stop()
        self.assertEqual(type(time), np.ndarray)

    def test_low_freq(self):
        dev = MpI(FakeInput, sampling_frequency=1)
        dev.start()
        sleep(2)
        time, data = dev.read()
        dev.stop()
        self.assertEqual(type(time), np.ndarray)

    def test_datatypes(self):
        dev = MpI(FakeInput, data_shape=[[3]], data_type=[ctypes.c_uint16])
        dev.start()
        sleep(0.5)
        time, data = dev.read()
        dev.stop()
        self.assertEqual(data.dtype, 'uint16')

    def test_het_datatypes(self):
        dev = MpI(HetInput)
        dev.start()
        sleep(0.5)
        time, data = dev.read()
        dev.stop()
        self.assertEqual(data[0].dtype, '|S1')
        self.assertEqual(data[1].dtype, 'uint16')

    def test_small_buffer(self):
        dev = MpI(FakeInput, nrow=2, sampling_frequency=1000)
        dev.start()
        sleep(1)
        time, data = dev.read()
        self.assertEqual(data.shape, (2, 5))
        diff = np.diff(time)
        print(time)
        print(data)
        dev.stop()
        self.assertTrue(np.isclose(diff, 0.001, atol=1e-2))

    def test_multi_devices(self):
        dev1 = MpI(FakeInput)
        dev2 = MpI(FakeInput)
        dev1.start()
        dev2.start()
        sleep(0.5)
        ti1, da1 = dev1.read()
        ti2, da2 = dev2.read()
        dev1.stop()
        dev2.stop()
        self.assertEqual(da1.shape, da2.shape)
