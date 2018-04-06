# Input Devices

One of the goals of `toon` is to simplify the process of polling input devices.

There are two parts to the `toon` device arrangement--the input device (inheriting from `toon.input.base_input.BaseInput`, and the multiprocessing wrapper, found in `toon.input.mp_input`. The user should not need to worry about the internals of the `MultiprocessInput` class (though see the section below about limitations). As long as the user implements an interface that matches `BaseInput`, the whole system should Just Work™.

A typical session with this arrangement might look something like:

```python
import MyDevice
from toon.input import MultiprocessInput

dev = MultiprocessInput(MyDevice, sampling_frequency=100, <other kwargs>)

with dev as d:
    while True:
        time, data = d.read()
        if time is not None:
            # do something with time/data
        # do other things

```


## Implementing a Device

There are four methods necessary for a complete device (and enforced via the `abc` module).

- `__init__()`
  - Can specify a different clock source here (via the `clock` keyword argument). I've borrowed `psychopy`'s `clock.MontonicClock` (minus the pyglet import) to use as the default.
  - Pass in other keyword args too, like sampling frequency, various device-specific flags, etc.
- `__enter__()`
  - Start communication with the device here.
  - Remember to `return self` at the end!
- `read()`
  - Returns a `(time, data)` tuple, where `time` is the output of `self.clock()`, and `data` is either a scalar, a `numpy.array`, or a list of either.
- `__exit__()`
  - Put the device in a good state (only if necessary). This will be called regardless of how the program exits.

There are also three static methods that take all keyword arguments. These are used by the multiprocessing machinery to preallocate the shared memory arrays. These are methods, rather than properties or something more static, to allow for devices with flexible outputs (e.g. trakSTAR and Flock of Birds).

- `samp_freq(**kwargs)` (returns scalar)
  - Infers the sampling frequency.
- `data_shapes(**kwargs)` (returns list of lists)
  - Infers the shape of data for a single `read` call.
- `data_types(**kwargs)` (returns list)
  - Infers the data type for each element of `data_shapes`.

We use the context manager construct for input devices, so that in the case of catastrophic failure, our device can be returned to a desirable state. This doesn't matter for all devices; for example, the mouse and keyboard don't have any particular state, so we leave our `__exit__()` method blank. However, devices like the Flock of Birds **do** have idle/sampling states to toggle, and leaving them configured and running after failure of the experiment can lead to headaches when restarting/reconnecting.

I've worked out a few examples, which cover straightforward implementations (`Hand`), and slightly hairier situations (`ForceKeyboard`, `Mouse` and `Keyboard`).

`Hand`:
 - One of our in-house devices, which gives us 3-DoF isometric forces for all fingers via a human interface device (HID).
 - Nothing too tricky--single data source, minimal configuration (at time of writing), and easy cleanup.

`ForceKeyboard`:
 - A predecessor to `Hand`; gives us 1-DoF forces and communication via a National Instruments DAQ.
 - `nidaqmx.Task` is already a context manager, so we need to subsume that machinery into our own. We end up calling `start()`, `stop()`, and `close()` manually from our own `__enter__()` and `__exit__()`.
 
`Mouse`:
 - The package I use for mouse functionality (`pynput`) spawns a thread for checking the mouse state, so we have to again take care of the context manager functionality.
 - Additionally, `pynput` uses callbacks to give us data, so we use `on_move()` to append new data to a list, and the `read()` function to copy data out of that list for consumption.
 - There are two unresolved issues:
   - We can't handle if there have been >1 move events since the last `read()` on the multiprocessing side (very unlikely). As a workaround, I just take the last element of the list as the singular reading.
   - We don't record things like button presses and scroll wheel activity in the same device. I'm not entirely sure how I want to deal with independent data sources from the same device (see limitations below).

`Keyboard`:
 - Same as `Mouse`, minus the issues with independent data sources (everything comes in largely the same format).
 - This was a good test of returning different data types.


## Limitations

### Batched data sources
Currently, I don't have a great way to handle devices that send batched data (i.e. more than one data point at a time). It's possible to work around this by adding dimensions to your data output (e.g. return a 1x3 array), but this would only work if the number of data points in the batch is consistent. I *think* we should be able to come up with an expected output structure that the multiprocessing side can iterate over, but I just haven't spent enough time thinking about it.

### Heterogeneous data sources (TODO: clarify)
There also isn't structure for devices that can return data from multiple (independent) sources, e.g. computer mice. However, if the state is returned in lock-step (i.e. we get the button states, position, and scroll wheel state simultaneously), then we can just specify multiple `data_shapes`/`data_types` when writing our new device.

## How `MultiprocessInput` Works

`MultiprocessInput` takes a device defined as above, and polls it incessantly until the main process signals to stop. Data is added to one or multiple `multiprocessing.Array`s, and access to the data is controlled via a single `multiprocessing.RLock`. The default size of the shared array is `ceil(10 * (device sampling rate/60)) * <product of all other dims>`, which is ~10x the amount of data we would expect in a single frame. If that size is not sufficient, you can manually set the number of rows by the `nrow` argument during initialization. For convenience, we interpret the shared array as a numpy array via `numpy.frombuffer`, which allows us to use indexing/functions from numpy.

If the shared array is filled, we replace the oldest data with the newest (via `numpy.roll`). When the user wants to retrieve data, the `read` function returns a (timestamp, data) tuple, where timestamp is a 1-D numpy array, and data is either a single numpy array of arbitrary shape (except dimension 0 tracks time), or a list of numpy arrays (following the same rules). After the data is copied from shared arrays to local ones, we copy the value of and reset the counter used to track how many readings have occurred since the last `read()` call. We then use the copied value of the counter to subset our timestamps and data (anything beyond being garbage). If no data has come in, we return a `(None, None)` tuple.

We also try to bump the priority of the remote process and disable garbage collection by default, which ??may?? lead to better performance. I *think* the priority bump will fail if not running with elevated privileges, but it'll just silently fail.
