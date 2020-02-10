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
-   High-resolution clocks.

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
from mydevice.mouse import Mouse
from timeit import default_timer

device = MpDevice(Mouse())

with device:
    t1 = default_timer() + 10
    while default_timer() < t1:
        data = device.read()
        # alternatively, unpack
        # clicks, pos, scroll = device.read()
        if data is not None:
            time, data = data # unpack
            # N-D array of data (0th dim is time)
            print(data)
```

Creating a custom device is relatively straightforward, though there are a few boxes to check.

```python
from ctypes import c_double

class MyDevice(BaseDevice):
    # optional: give a hint for the buffer size (we'll allocate 1 sec worth of this)
    sampling_frequency = 500

    # this can either be introduced at the class level, or during __init__
    shape = (3, 3)
    # ctype can be a python type, numpy dtype, or ctype
    # including ctypes.Structures
    ctype = c_double

    # optional. Do not start device communication here, wait until `enter`
    def __init__(self):
        pass
    
    ## Use `enter` and `exit`, rather than `__enter__` and `__exit__`
    # optional: configure the device, start communicating
    def enter(self):
        pass
    
    # optional: clean up resources, close device
    def exit(self):
        pass
    
    # required
    def read(self):
        # See demos/ for examples of sharing a time source between the processes
        time = self.clock()
        # store new data with a timestamp
        data = get_data()
        return time, data
```

This device can then be passed to a `toon.input.MpDevice`, which preallocates the shared memory and handles other details.

A few things to be aware of for data returned by `MpDevice`:

 - If there's no data for a given observation, `None` is returned.


Other notes:
  - The returned data is a *copy* of the local copy of the data. If you don't need copies, set `copy_read=False` when instantiating the `MpDevice`.
  - If receiving batches of data when reading from the device, you can return a list of (time, data) tuples.
  - You can optionally use `device.start()`/`device.stop()` instead of a context manager.
  - You can check for remote errors at any point using `device.check_error()`, though this automatically happens after entering the context manager and when reading.
  - In addition to python types/dtypes/ctypes, devices can return `ctypes.Structure`s (see input tests or the [cyberglove](https://github.com/aforren1/toon/blob/master/toon/input/cyberglove.py) for examples).

### Animation

This is still a work in progress, though I think it has some utility as-is. It's a port of the animation component in the [Magnum](https://magnum.graphics/) framework, though lacking some of the features (e.g. Track extrapolation, proper handling of time scaling).

Example:

```python
from math import sin, pi

from time import sleep
from timeit import default_timer
import matplotlib.pyplot as plt
from toon.anim import Track, Player
# see toon/anim/easing.py for all available easings
from toon.anim.easing import linear

class Circle(object):
    x = 0
    y = 0

circle = Circle()
# list of (time, value)
keyframes = [(0.2, -0.5), (0.5, 0), (3, 0.5)]
x_track = Track(keyframes, easing=linear)

# currently, easings can be any function that takes a single
# positional argument as input (time normalized to [0, 1]) and returns
# a scalar (probably float), generally having a lower asymptote
# of 0 and upper asymptote of 1, which is used as the current time
# for purposes of interpolation
def elastic_in(x):
    return pow(2.0, 10.0 * (x - 1.0)) * sin(13.0 * pihalf * x)

# we can reuse keyframes
y_track = Track(keyframes, easing=elastic_in)

player = Player(repeats=3)

# directly modify an attribute
player.add(x_track, 'x', obj=circle)

def y_cb(val, obj):
    obj.y = val

# modify via callback
player.add(y_track, y_cb, obj=circle)

t0 = default_timer()
player.start(t0)
vals = []
while player.is_playing:
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

### Utilities

The `util` module includes high-resolution clocks/timers. Windows uses `QueryPerformanceCounter`, MacOS uses `mach_absolute_time`, and other systems use `timeit.default_timer`. The class is called `MonoClock`, and an instantiation called `mono_clock` is created upon import. Usage:

```python
from toon.util import mono_clock, MonoClock

clk = mono_clock # re-use pre-instantiated clock
clk2 = MonoClock(relative=False) # time relative to whenever the system's clock started

t0 = clk.get_time()
```

Another utility currently included is a `priority` function, which tries to improve the determinism of the calling script. This is derived from Psychtoolbox's `Priority` (doc [here](http://psychtoolbox.org/docs/Priority)). General usage is:

```python
from toon.util import priority

res = priority(1)
if not res:
    raise ValueError('Failed to raise priority.')

# ...do stuff...

priority(0)
```

The input should be a 0 (no priority/cancel), 1 (higher priority), or 2 (realtime). If the requested level is rejected, the function will return `False`. The exact implementational details depend on the host operating system. All implementations disable garbage collection.

#### Windows
 - Uses `SetPriorityClass` and `SetThreadPriority`/`AvSetMmMaxThreadCharacteristics`.
 - `level = 2` only seems to work if running Python as administrator.

#### MacOS
 - Only disables/enables garbage collection; I don't have a Mac to test on.

#### Linux
  - Sets the scheduler policy and parameters `sched_setscheduler`.
  - If `level == 2`, locks the calling process's virtual address space into RAM via `mlockall`.
  - Any `level > 0` seems to fail unless the user is either superuser, or has the right capability. I've used setcap: `sudo setcap cap_sys_nice=eip <path to python>` (disable by passing `sudo setcap cap_sys_nice= <path>`). For memory locking, I've used Psychtoolbox's [99-psychtoolboxlimits.conf](https://github.com/Psychtoolbox-3/Psychtoolbox-3/blob/master/Psychtoolbox/PsychBasic/99-psychtoolboxlimits.conf) and added myself to the psychtoolbox group.

Your mileage may vary on whether these *actually* improve latency/determinism. When in doubt, measure! Read the warnings [here](http://psychtoolbox.org/docs/Priority).

Notes about checking whether parts are working:

#### Windows
 - In the task manager under details, right-clicking on python and mousing over "Set priority" will show the current priority level. I haven't figured out how to verify the Avrt threading parts are working.

#### Linux
 - Check `mlockall` with `cat /proc/{python pid}/status | grep VmLck`
 - Check priority with `top -c -p $(pgrep -d',' -f python)`
