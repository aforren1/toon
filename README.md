toon
====

[![image](https://img.shields.io/pypi/v/toon.svg)](https://pypi.python.org/pypi/toon)
[![image](https://img.shields.io/pypi/l/toon.svg)](https://raw.githubusercontent.com/aforren1/toon/master/LICENSE.txt)
[![image](https://img.shields.io/travis/aforren1/toon.svg)](https://travis-ci.org/aforren1/toon)
[![image](https://img.shields.io/appveyor/ci/aforren1/toon.svg)](https://ci.appveyor.com/project/aforren1/toon)
[![image](https://img.shields.io/coveralls/aforren1/toon.svg)](https://coveralls.io/github/aforren1/toon)

Description
-----------

Additional tools for neuroscience experiments, including:

-   A framework for polling input devices on a separate process.
-   A framework for keyframe-based animation.

Everything should work on Windows/Mac/Linux.

See [requirements.txt](https://github.com/aforren1/toon/blob/master/requirements.txt) for dependencies.

Install
-------

Current release:

```pip install toon```

Development version:

```pip install git+https://github.com/aforren1/toon```

For full install (including device and demo dependencies):

```pip install toon[full]```

See [setup.py](https://github.com/aforren1/toon/blob/master/setup.py) for a list of those dependencies, as well as device-specific subdivisions.

See the [demos/](https://github.com/aforren1/toon/tree/master/demos) folder for usage examples (note: some require [psychopy](https://github.com/psychopy/psychopy)).

Overview
---------

### Input

`toon` provides a framework for polling from input devices, including common peripherals like mice and keyboards, with the flexibility to handle less-common devices like eyetrackers, motion trackers, and custom devices (see `toon/input/` for examples). The goal is to make it easier to use a wide variety of devices, including those with sampling rates >1kHz, with minimal performance impact on the main process.

We use the built-in `multiprocessing` module to control a separate process that hosts the device, and, in concert with `numpy`, to move data to the main process via shared memory. It seems that under typical conditions, we can expect single `read()` operations to take less than 500 microseconds (and more often < 100 us). See [demos/bench.py](https://github.com/aforren1/toon/blob/master/demos/bench.py) for an example of measuring user-side read performance.

Typical use looks like this:

```python
from toon.input import MpDevice
from toon.input.mouse import Mouse
from timeit import default_timer

device = MpDevice(Mouse())

with device:
    t1 = default_timer() + 10
    while default_timer() < t1:
        data = device.read()
        # alternatively, unpack
        # clicks, pos, scroll = device.read()
        if data.pos is not None:
            # N-D array of data (0th dim is time)
            print(data.pos)
            # time is 1D array of timestamps
            print(data.pos.time)
            print(data.pos[-1].time) # most recent timestamp
```

Creating a custom device is relatively straightforward, though there are a few boxes to check.

```python
from toon.input import BaseDevice, make_obs
from ctypes import c_double

# Obs is a class that manages observations
class MyDevice(BaseDevice):
    # optional: give a hint for the buffer size (we'll allocate 1s worth of this)
    sampling_frequency = 500

    # required: each data source gets its own Obs
    # can have multiple Obs per device
    # this can either be introduced at the class level, or during __init__
    # ctype can be a python type, numpy dtype, or ctype
    Pos = make_obs('Pos', shape=(3,), ctype=float)
    RotMat = make_obs('RotMat', (3, 3), c_double) # 2D data

    # optional. Do not start device communication here, wait until `enter`
    def __init__(self):
        pass
    
    ## Use `enter` and `exit`, rather than `__enter__` and `__exit__`
    # optional: configure the device, start communicating
    def enter(self):
        pass
    
    # optional: clean up resources, close device
    def exit(self, *args):
        pass
    
    # required
    def read(self):
        # See demos/ for examples of sharing a time source between the processes
        time = self.clock()
        # store new data with a timestamp
        pos = self.Pos(time, (1, 2, 3))
        rotmat = self.RotMat(time, [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        # can also be explicit, i.e. `self.Returns(pos=pos, rotmat=rotmat)`
        return pos, rotmat
```

This device can then be passed to a `toon.input.MpDevice`, which preallocates the shared memory and handles other details.

A few things to be aware of for data returned by `MpDevice`:

 - If a device only has a single `Obs`, `MpDevice` returns a single `TsArray` (a numpy array with a `time` attribute). Otherwise, `MpDevice` returns a named tuple of observations, where the names are alphabetically-sorted, lowercased versions of the pre-defined `Obs`. 
 - If the data returned by a single read is scalar (e.g. a 1D force sensor), `MpDevice` will drop the 1st dimension.
 - If there's no data for a given observation, `None` is returned. The named tuple has a method for checking all members at once (`data.any()`).


Other notes:
  - The returned data is a *view* of the local copy of the data. `toon.input.TsArray`s and device `Returns` have a `copy` method, which may be useful if e.g. appending to a list for later concatenation.
  - Re: concatenation, there is a `stack` function available via `from toon.input import stack`, which is like numpy's `vstack` but keeps the time attribute intact. It also dispatches appropriately for either `TsArray`s or `Returns`.
  - If receiving batches of data when reading from the device, you can return a list of `Returns` (see `tests/input/mockdevices.py` for an example).
  - You can optionally use `device.start()`/`device.stop()` instead of a context manager.
  - You can check for remote errors at any point using `device.check_error()`, though this automatically happens after entering the context manager and when reading.
  - In addition to python types/dtypes/ctypes, `Obs` can use `ctypes.Structure`s (see input tests or the [cyberglove](https://github.com/aforren1/toon/blob/master/toon/input/cyberglove.py) for examples).

### Animation

This is still a work in progress, though I think it has some utility as-is. It's a port of the animation component in the [Magnum](https://magnum.graphics/) framework, though lacking some of the features (e.g. Track extrapolation, proper handling of time scaling).

Example:

```python
from time import sleep
from timeit import default_timer
import matplotlib.pyplot as plt
from toon.anim import Track, Player
# see toon/anim/easing.py for all easings available
from toon.anim.easing import linear, elastic_in_out

class Circle(object):
    x = 0
    y = 0

circle = Circle()
# list of (time, value)
keyframes = [(0.2, -0.5), (0.5, 0), (3, 0.5)]
x_track = Track(keyframes, easing=linear)
# we can reuse keyframes
y_track = Track(keyframes, easing=elastic_in_out)

player = Player()

# directly modify an attribute
player.add(x_track, 'x', obj=circle)

def y_cb(val, obj):
    obj.y = val

# modify via callback
player.add(y_track, y_cb, obj=circle)

t0 = default_timer()
player.start(t0)
vals = []
while default_timer() < t0 + 3.2:
    player.advance(default_timer())
    vals.append([circle.x, circle.y])
    sleep(1/60)

plt.plot(vals)
plt.show()
```

Other notes:
  - Non-numeric attributes, like color strings, can also be modified in this framework (easing is ignored).
  - The `Timeline` class (in `toon.anim`) can be used to get the time between frames, or the time since some origin time, taken at `timeline.start()`.
  - The `Player` can also be used as a mixin, in which case the `obj` argument can be omitted from `player.add()` (see the [demos/](https://github.com/aforren1/toon/tree/master/demos) folder for examples).
  - Multiple objects can be modified simultaneously by feeding a list of objects into `player.add()`.
