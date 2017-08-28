import ctypes
import multiprocessing as mp
import struct
import numpy as np
import hid


def shared_to_numpy(mp_arr, nrow, ncol):
    """Helper to allow use of a multiprocessing.Array as a numpy array"""
    return np.frombuffer(mp_arr.get_obj()).reshape((nrow, ncol))


class DummyTime(object):
    """
    Stand-in for psychopy timer.

    Just provides a `getTime` method that returns 0,
    so that we can run the device without having psychopy fully installed.
    """
    def getTime(self):
        return 0


class Hand(object):
    """
    A class that handles communication with HAND.

    Example usage:

    from hand import Hand
    import psychopy.core

    monotime = psychopy.core.monotonicClock
    dev = Hand(time=monotime, multiproc=True)
    
    dev.start()
    data = dev.read() # returns buffer since last read
    dev.stop() # stop device
    dev.start() # re-open device
    dev.close() # also calls dev.stop()
    """

    def __init__(self, time=DummyTime(), buffer_rows=50, multiproc=False, nonblocking=True):
        """
        If `multiproc` is True, sets up remote interface for polling the device.
        The size of the shared buffer can be set via `buffer_rows`.

        `time` should be a copy of psychopy.core.monotonicClock (though I don't enforce that currently).
        `nonblocking` determines whether the HID blocks the thread while waiting for input.

        Note that the default settings are conservative (no multiprocessing, no blocking).
        """
        self._ncol = 17
        self._nrow = buffer_rows
        self._device = None
        self.multiproc = multiproc
        self._force_data = np.full(self._ncol, np.nan)
        self._rot_val = np.pi / 4.0
        self._sinval = np.sin(self._rot_val)
        self._cosval = np.cos(self._rot_val)
        self._time = time
        self.nonblocking = nonblocking

        if multiproc:
            self._shared_mp_buffer = mp.Array(ctypes.c_double, self.nrow * self.ncol)
            self._shared_np_buffer = shared_to_numpy(self._shared_mp_buffer, self.nrow, self.ncol)
            self._shared_np_buffer.fill(np.nan)
            self._read_buffer = np.full((self.nrow, self.ncol), np.nan)
            self._poison_pill = mp.Value(ctypes.c_bool)
            self._poison_pill.value = True
            self._process = None

    def start(self):
        """
        If multiproc is True, start the remote process (see worker()). 
        Otherwise, open the HID communication.
        """
        if self.multiproc:
            self._poison_pill.value = True
            self.clear()
            self._process = mp.Process(target=self.worker)
            self._process.daemon = True
            self._process.start()
        else:
            self._device = hid.device()
            self._device.open(0x16c0, 0x486)
            self._device.set_nonblocking(self.nonblocking)

    def stop(self):
        """ If multiproc is True, stop the remote process (does nothing otherwise)."""
        if self.multiproc:
            self._poison_pill.value = False

    def close(self):
        """ Close the HID interface."""
        self.stop()
        if not self.multiproc:
            self._device.close()

    def read(self):
        """
        Returns a single reading (multiproc=False) or the all values stored
        in the shared buffer (multiproc=True).
        If no data, returns None (multiproc=False and True).

        Each row is formatted as follows:
        [psychopy_time, HAND_time, x1, y1, z1, x2, y2, z2, x3...]
        """
        # TODO: return both x,y,z (based on median) AND raw data?
        if self.multiproc:
            np.copyto(self._read_buffer, self._shared_np_buffer)
            self.clear()
            if np.isnan(self._read_buffer).all():
                return None
            return self._read_buffer[~np.isnan(self._read_buffer).any(axis=1)]
        return self._read()

    def _read(self):
        """ Core read function. Please use read(), which abstracts away the multiprocessing parts."""
        data = self._device.read(46)
        if data:
            data = struct.unpack('>LhHHHHHHHHHHHHHHHHHHHH', bytearray(data))
            data = np.asarray(data, dtype='d')
            data[0] /= 1000.0
            data[1:] /= 65535.0
            self._force_data[0] = self._time.getTime()  # game time
            self._force_data[1] = data[0]  # HAND's personal time
            self._force_data[2::3] = data[2::4] * self._cosval - data[3::4] * self._sinval  # x
            self._force_data[3::3] = data[2::4] * self._sinval + data[3::4] * self._cosval  # y
            self._force_data[4::3] = data[4::4] + data[5::4]  # z
            return self._force_data
        return None

    def write(self):
        """ Write to device. Will be used to set sampling frequency, amplifier gains, etc."""
        raise NotImplementedError('Alex needs to implement this.')

    def clear(self):
        """ Clear the shared buffer. """
        with self._shared_mp_buffer.get_lock():
            self._shared_np_buffer.fill(np.nan)

    def worker(self, shared_buffer):
        """ Workhorse for polling the device on a remote process."""
        self._device = hid.device()
        self._device.open(0x16c0, 0x486)
        self._device.set_nonblocking(self.nonblocking)
        # (try to) clear buffer
        for i in range(50):
            self._read()
        # loop until poison pill toggled
        while self._poison_pill.value:
            data = self._read()
            if data is not None:
                with self._shared_mp_buffer.get_lock():
                    current_nans = np.isnan(self._shared_np_buffer).any(axis=1)
                    if current_nans.any():
                        next_index = np.where(current_nans)[0][0]
                        self._shared_np_buffer[next_index, :] = data
                    else:
                        self._shared_np_buffer[:] = np.roll(self._shared_np_buffer, -1, axis=0)
                        self._shared_np_buffer[-1, :] = data
        self._device.close()


if __name__ == '__main__':
    import psychopy.core

    time = psychopy.core.monotonicClock
    dev = Hand(time=time, multiproc=True)
    dev.start()
    psychopy.core.wait(0.016, hogCPUperiod=0.016)
    for ii in range(10):
        data = dev.read()
        print(data[:, 0])
        print(data[:, 1])
        psychopy.core.wait(0.016, hogCPUperiod=0.016)

    dev.close()
