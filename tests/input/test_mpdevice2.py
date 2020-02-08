from time import sleep
from pytest import raises, approx
import numpy as np
from tests.input.mockdevices import Dummy, Timebomb, DummyList, SometimesNot, StructObs
from toon.util import mono_clock
from toon.input import MpDevice


def test_device_single():
    dev = MpDevice(Dummy())
