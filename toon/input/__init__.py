from toon.input.mpdevice import MpDevice
from toon.input.device import BaseDevice, Obs, make_obs
from toon.input.clock import mono_clock, MonoClock
from toon.input.tsarray import stack as tsstack
from toon.input.mpdevice import stack as retstack
from toon.input.tsarray import TsArray


def stack(tup):
    if tup == []:
        raise ValueError('Empty list of Observations or Returns.')
    if isinstance(tup[0], TsArray):
        return tsstack(tup)
    return retstack(tup)
