import ctypes
import multiprocessing as mp
import struct
import numpy as np
import hid
import psychopy.core

def shared_to_numpy(mp_arr, nrow, ncol):
    return np.frombuffer(mp_arr.get_obj()).reshape((nrow,ncol))

class Hand(object):
    """
    A class that handles communication with HAND.

    Example usage:

    from hand import Hand
    dev = Hand(multiproc=True)
    
    dev.start()

    data = dev.read() # returns buffer since last read

    dev.stop() # stop device

    dev.start() # re-open device

    dev.close() # also calls dev.stop()

    """
    def __init__(self, buffer_rows=50, multiproc=False):
        """
        If multiproc is True, sets up remote interface for polling the device.
        The size of the shared buffer can be set via buffer_rows.

        """
        self.ncol = 16
        self.nrow = buffer_rows
        self._device = None
        self.multiproc = multiproc
        self._force_data = np.full(16, np.nan)
        self._rot_val = np.pi / 4.0

        if multiproc:
            self._shared_buffer = mp.Array(ctypes.c_double, self.nrow*self.ncol)
            self.shared_buffer = shared_to_numpy(self._shared_buffer, self.nrow, self.ncol)
            self.shared_buffer.fill(np.nan)
            self.read_buffer = np.full((self.nrow, self.ncol), np.nan)
            self.poison_pill = mp.Value(ctypes.c_bool)
            self.poison_pill.value = True

    def start(self):
        """
        If multiproc is True, start the remote process. Otherwise, open the HID communication.
        """
        if self.multiproc:
            self.poison_pill.value = True
            self.clear()
            self.process = mp.Process(target=self.worker,
                                      args=(self._shared_buffer, self.poison_pill,
                                            self.nrow, self.ncol))
            self.process.start()
        else:
            self._device = hid.device()
            self._device.open(0x16c0, 0x486)
            self._device.set_nonblocking(1)
    
    def stop(self):
        """
        If multiproc is True, stop the remote process (does nothing otherwise).
        """
        if self.multiproc:
            self.poison_pill.value = False
    
    def close(self):
        """
        Close the HID interface.
        """
        self.stop()
        if not self.multiproc:
            self._device.close()
    
    def read(self):
        """
        Returns a single reading (multiproc=False) or the all values stored
        in the shared buffer (multiproc=True).

        If no data, returns None (multiproc=False and True).
        """
        # TODO: return both x,y,z (based on median) AND raw data
        if self.multiproc:
            np.copyto(self.read_buffer, self.shared_buffer)
            self.clear()
            if np.isnan(self.read_buffer).all():
                return None
            return(self.read_buffer[~np.isnan(self.read_buffer).any(axis=1)])
        return self._read()
    
    def _read(self):
        """
        Core read function. Please use read(), which abstracts away the multiprocessing parts.
        """
        data = self._device.read(46)
        if data:
            data = struct.unpack('>LhHHHHHHHHHHHHHHHHHHHH', bytearray(data))
            data = np.asarray(data, dtype='d')
            data[0] /= 1000.0
            data[1:] /= 65535.0
            self._force_data[0] = data[0]
            self._force_data[1::3] = data[2::4] * np.cos(self._rot_val) - data[3::4] * np.sin(self._rot_val) # x
            self._force_data[2::3] = data[2::4] * np.sin(self._rot_val) + data[3::4] * np.cos(self._rot_val) # y
            self._force_data[3::3] = data[4::4] + data[5::4] # z
            return(self._force_data)
        return(None)

    def write(self):
        """
        Write to device. Will be used to set sampling frequency, amplifier gains, etc.
        """
        raise NotImplementedError('Alex needs to implement this.')
    
    def clear(self):
        """
        Clear the shared buffer.
        """
        self.shared_buffer.fill(np.nan)
    
    def worker(self, shared_buffer, poison_pill, nrow, ncol):
        """
        Workhorse for polling the device on a remote process.
        """
        self._device = hid.device()
        self._device.open(0x16c0, 0x486)
        self._device.set_nonblocking(1)
        # (try to) clear buffer
        arr = shared_to_numpy(shared_buffer, nrow, ncol)
        for i in range(50):
            self.read()
        while poison_pill.value:
            data = self._read()
            if data is not None:
                with shared_buffer.get_lock():
                    current_nans = np.isnan(arr).any(axis=1)
                    if current_nans.any():
                        next_index = np.where(current_nans)[0][0]
                        arr[next_index,:] = data
                    else:
                        arr[:] = np.roll(arr, -1, axis=0)
                        arr[next_index,:] = data
        self._device.close()
