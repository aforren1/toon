import ctypes
import multiprocessing as mp
import struct
import numpy as np
import hid
import psychopy.core

def shared_to_numpy(mp_arr, nrow, ncol):
    return np.frombuffer(mp_arr.get_obj()).reshape((nrow,ncol))


class KataHand(object):
    def __init__(self, buffer_rows=50):
        self.ncol = 2
        self.nrow = buffer_rows
        self._shared_buffer = mp.Array(ctypes.c_double, self.nrow*self.ncol)
        self.shared_buffer = shared_to_numpy(self._shared_buffer, self.nrow, self.ncol)
        self.shared_buffer.fill(np.nan)
        self.read_buffer = np.full((self.nrow, self.ncol), np.nan)

        self.poison_pill = mp.Value(ctypes.c_bool)
        self.poison_pill.value = True

    def start(self):
        self.poison_pill.value = True
        self.clear()
        self.process = mp.Process(target=self.worker,
                                  args=(self._shared_buffer, self.poison_pill,
                                        self.nrow, self.ncol))
        self.process.start()
    
    def stop(self):
        self.poison_pill.value = False
    
    def read(self):
        # TODO: return both x,y,z (based on median) AND raw data
        self.read_buffer[:] = self.shared_buffer
        self.clear()
        return(self.read_buffer)

    def write(self):
        raise NotImplementedError('Alex needs to implement this.')
    
    def clear(self):
        self.shared_buffer.fill(np.nan)
    
    def worker(self, shared_buffer, poison_pill, nrow, ncol):
        while poison_pill.value:
            with shared_buffer.get_lock():
                arr = shared_to_numpy(shared_buffer, nrow, ncol)
                current_nans = np.isnan(arr).any(axis=1)
                if current_nans.any():
                    next_index = np.where(current_nans)[0][0]
                    arr[next_index,0] = psychopy.core.getTime()
                    arr[next_index,1] = np.random.random()
                else:
                    arr[:] = np.roll(arr, -1, axis=0)
                    arr[-1,0] = psychopy.core.getTime()
                    arr[-1,1] = np.random.random()
                psychopy.core.wait(0.000001)

if __name__=='__main__':
    hd = KataHand(buffer_rows=100)

    hd.start()
    for ii in range(50):
        print(hd.read())
        psychopy.core.wait(0.16)
    hd.stop()
