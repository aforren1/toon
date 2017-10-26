# Input Devices

One of the goals of `toon` is to simplify the process of polling input devices.

# Device Implementation

When implementing a new device, it may be the most straightforward to inherit from `toon.input.BaseInput`. This will ensure that all the necessary methods are written. To manage device state, we'll use a context manager -- this will allow us to leave the device in a desirable state, even if the experiment exits unexpectedly. 

The four methods to implement are:

 - `__init__`: Collect the timing source for the device (by default, `timeit.default_timer`) and other settings for that particular device (e.g. screen dimensions, keys of interest, sampling frequency)
 - `__enter__`: Begin communication with the device, apply any necessary settings, and ask the device to begin sending data. Make sure to `return self` at the end of this function!
 - `read`: The read function for the device, which returns one measurement. Generally, I'll return a dictionary with the current time and one observation, e.g. `{'time': self.time(), 'data': self._device.read()}`. However, you are free to return whatever you'd like.
 - `__exit__`: Place the input device in a desirable state (e.g. stop sampling, place in standby mode) and terminate the connection.
 

In my experience, examples are worth several thousand words. In this package, we include implementations of several devices, ranging from simple (`toon.input.Hand`) to the complicated (`toon.input.BlamBirds`), and spanning many input channels (raw Serial, USB/HID, DAQs). Current examples are listed below:

 - `BlamBirds`: Communicate with the Flock of Birds from Ascension via `pyserial`.
 - `ForceTransducers`: Communicate with several analog sensors (force transducers) via `nidaqmx`.
 - `Hand`: HID interface to another custom lab device, via `hidapi`. The device is a 
 - `Keyboard`: Uses `pynput` to communicate with the keyboard.
 
Only the `Keyboard` is generally available (the others being in-house devices at the BLAM Lab). However, 

Next, we'll explore polling the device on a separate process. This is invaluable for high-frequency devices, where the rate at which new data arrives exceeds the screen refresh rate.

# Multiprocessing Implementation

