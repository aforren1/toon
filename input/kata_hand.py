import ctypes
import multiprocessing as mp
import struct
import numpy as np
import hid
import psychopy.core

def shared_to_numpy(mp_arr, nrow, ncol):
    return np.frombuffer(mp_arr.get_obj()).reshape((nrow,ncol))

def worker(remote_buffer, poison_pill, nrow, ncol, clock, wait):
    # set poison_pill.value to False to end worker
    while poison_pill.value:
        with remote_buffer.get_lock():
            # convert to numpy array for more friendly modifications
            arr = shared_to_numpy(remote_buffer, nrow, ncol)
            # get first non-nan row
            #bytes_from_dev = d.read(64)
            #arr[i] = struct.unpack('>LHH', bytes_from_dev)
            current_nans = np.isnan(arr).any(axis=1)
            if current_nans.any():
                next_index = np.where(current_nans)[0][0]
                arr[next_index, 0] = clock()
                arr[next_index, 1] = np.random.random()
            else:
                arr[:] = np.roll(arr, -1, axis=0)
                arr[-1,0] = clock()
                arr[-1,1] = np.random.random()
            wait(1)


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

    p = mp.Process(target=worker, args=(remote_buffer, poison_pill, nrow, ncol, clock, wait))
    p.start()
    wait(14)

    result = shared_to_numpy(remote_buffer, nrow, ncol)
    print(result)
    poison_pill.value = False

# get the numpy array out as
