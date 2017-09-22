Input Devices in toon
=====================

This document describes how the input devices in :mod:`toon.input` operate.

The Base Class
--------------

There is an abstract base class (derived from :mod:`abc`) defined in :mod:`toon.input.base_input`, called :class:`BaseInput`. This provides structure for polling input devices on a separate process, via the :mod:`multiprocessing` module. This allows us to poll devices at high frequency -- for instance, the derived class :class:`Hand` polls a custom Human Interface Device at 1 kHz. Additionally, each measurement
receives a timestamp (by default :func:`time.time()`, but more preferably :func:`psychopy.core.monotonicClock.getTime()`). The key thing is the ability to share a clock with the main process, so that inter-frame events from the input device are related properly to events in the main process.

..image:: res/flow_diagram.png

Derived Classes
---------------

Derived classes must implement the following methods:

- `__init__`, for object-specific initialization and settings
- `_init_device`, for device creation (e.g. `serial.Serial()`)
- `_read`, for reading a single measurement from the device (e.g. `serial.readline()`)
    - Should return a tuple (measurement, time), where measurement is a n-dimensional array, and time is a scalar.
    - Should return (None, None) if no data available.
- `_stop_device`, to stop device measurements
- `_close_device`, to close the device connection (e.g. `serial.close()`)

Though it may be necessary to retool other methods for your particular use case.

Misc notes:
-----------

- `_poison_pill` property is probably a misnomer (we're just toggling a flag)
- Should call `_stop_device` and `_close_device` when the session ends if they haven't been called yet (so that the devices aren't left in weird states)
