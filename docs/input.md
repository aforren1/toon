# Input Devices

One of the primary goals of `toon` is to simplify the process of polling input devices.

## Usage

See the toon/input directory for device specification and usage examples, and demos/mouse.py for a psychopy integration example.

Typical use of the input module may look like:

```python
import MyDevice
from toon.input.mpdevice import MpDevice

# specify keyword args for the device here
dev = MpDevice(MyDevice, foo=3, bar='baz')

with dev:
    while True:
        data = dev.read()
        if data.any():
            # do something
            pass

```

For easier incorporation with existing scripts, you can directly use `MpDevice.start()` and `stop()` rather than as a context manager.

The data returned by `read()` is a named tuple (one name per data coming in) of named tuples (always `time` and `data`). For example, the mouse example returns something like:

```python
Returns(clicks=obs(time=array([10.0311837]), 
                   data=array([[False]])), 
        pos=obs(time=array([10.03811626, 10.04504504]), 
                data=array([[ 2, -4], [ 3, -4]], dtype=int32)),
        scroll=obs(time=None, data=None))
```

So to access the most recent change in `pos`, the user can use `data.pos.data[-1]`. Named tuples also unpack, so you can also do something like `clicks, pos, scroll = mouse.read()`.

The `Returns` object returned by `read()` also has an `any()` method, which allows simpler checking for any worthwhile data.

The buffer size resolves in this order:

`buffer_len` > `sampling_frequency` in kwargs > `sampling_frequency` in device class

For example, in anticipation of a long sampling period (e.g. 3 second delay) with a high-frequency device (e.g. 1 kHz), the user can pass a `buffer_len=3000` to `MpDevice` (or perhaps more, for a safety margin).

Depending on the application, it may not be important to have *every* data point from the device. To that end, all shared arrays act as ring buffers-- once the buffer is full, the oldest value is replaced with the newest one. The newest data point can be accessed via `data.<name>.data[-1]`.

## Implementing a device

A new device needs the following (see examples in toon/input as ref):
  - One or more `Obs`-derived data class declarations under class attributes
  - `__enter__` for device instantiation/setup
  - `read` to move data from the device to Python

Other nice-to-haves:
  - `__init__` for setting up device resources
  - `sampling_frequency` attribute, for proper sizing of buffers
  - `__exit__` for device cleanup


The `Obs`-derived classes are straightforward to specify. For example, a mouse might have:

```python
from toon.input.device import BaseDevice, Obs
import ctypes

class Mouse(BaseDevice):
    class Pos(Obs):
        shape = (2,)
        ctype = ctypes.c_int

    class Clicks(Obs):
        shape = (1,)
        ctype = ctypes.c_bool

    class Scroll(Obs):
        shape = (1,)
        ctype = ctypes.c_int
    
    # rest of device specification here
    # ...
```

The guts of `BaseDevice` pick out all of the `Obs`-derived attributes, and build a custom `Returns` named tuple for the device, where names are the `.lower()`ed class names. Note that the `Obs` will appear in **alphabetical** order in `Returns`, not in order of specification.

The `read` method is somewhat finicky (see below for example usage).

```python
class Mouse(BaseDevice):
    # Obs here

    def read(self):
        time = self.clock()
        position = self.Pos(time, [3, 2])
        return self.Returns(pos=position, ...)
```

The `clock` attribute is a reference to some time method (by default `monotonic_clock.get_time` from `toon.input.clock`, other popular ones may be `psychopy.clocks.monotonicClock.getTime` or `timeit.default_timer`). We create a new set of tuples for each input, and put all those into a final `Returns` (which is dynamically created by `BaseDevice` to match the device).

Note that a 1D output must be in a form equivalent to `(x,)`, rather than `x` or `(x)`.

The data type can be one from `ctypes`, a `dtype` from numpy, or a built-in Python type.
