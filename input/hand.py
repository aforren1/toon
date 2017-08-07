import ctypes
import multiprocessing as mp
import struct
import numpy as np
import hid
import psychopy.core

def shared_to_numpy(mp_arr, nrow, ncol):
    return np.frombuffer(mp_arr.get_obj()).reshape((nrow,ncol))


class Hand(object):
    def __init__(self, buffer_rows=50, multiproc=True):
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
        if self.multiproc:
            self.poison_pill.value = False
    
    def close(self):
        self.stop()
        if not self.multiproc:
            self._device.close()
    
    def read(self):
        # TODO: return both x,y,z (based on median) AND raw data
        if self.multiproc:
            np.copyto(self.read_buffer, self.shared_buffer)
            self.clear()
            return(self.read_buffer)
        return self._read()
    
    def _read(self):
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
        raise NotImplementedError('Alex needs to implement this.')
    
    def clear(self):
        self.shared_buffer.fill(np.nan)
    
    def worker(self, shared_buffer, poison_pill, nrow, ncol):
        self._device = hid.device()
        self._device.open(0x16c0, 0x486)
        self._device.set_nonblocking(1)
        while poison_pill.value:
            data = self._read()
            if data is not None:
                with shared_buffer.get_lock():
                    arr = shared_to_numpy(shared_buffer, nrow, ncol)
                    current_nans = np.isnan(arr).any(axis=1)
                    if current_nans.any():
                        next_index = np.where(current_nans)[0][0]
                        arr[next_index,:] = data
                    else:
                        arr[:] = np.roll(arr, -1, axis=0)
                        arr[next_index,:] = data
        self._device.close()
