"""
Scratch work for polling on a separate process.
See hand.py for an example implementation.
"""

import ctypes
import multiprocessing as mp
import struct
import numpy as np
import hid
import psychopy.core


def shared_to_numpy(mp_arr, nrow, ncol):
    return np.frombuffer(mp_arr.get_obj()).reshape((nrow,ncol))


def worker(remote_buffer, poison_pill, nrow, ncol):
    # set poison_pill.value to False to end worker
    while poison_pill.value:
        with remote_buffer.get_lock():
            # convert to numpy array for more friendly modifications
            arr = shared_to_numpy(remote_buffer, nrow, ncol)
            current_nans = np.isnan(arr).any(axis=1)
            if current_nans.any():
                next_index = np.where(current_nans)[0][0]
                arr[next_index, 0] = psychopy.core.getTime()
                arr[next_index, 1] = np.random.random()
            else: # roll array around, replace oldest value
                arr[:] = np.roll(arr, -1, axis=0)
                arr[-1,0] = psychopy.core.getTime()
                arr[-1,1] = np.random.random()
            psychopy.core.wait(0.5)


if __name__=='__main__':
    nrow = 10
    ncol = 2
    remote_buffer = mp.Array(ctypes.c_double, nrow*ncol)

    arr = shared_to_numpy(remote_buffer, nrow, ncol)
    arr.fill(np.nan)

    poison_pill = mp.Value(ctypes.c_bool)
    poison_pill.value = True
    clock = psychopy.core.getTime
    wait = psychopy.core.wait

    p = mp.Process(target=worker, args=(remote_buffer, poison_pill, nrow, ncol))
    p.start()
    wait(5)

    print(arr)
    arr.fill(np.nan)
    print(arr)
    poison_pill.value = False
