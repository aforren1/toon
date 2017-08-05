import ctypes
import multiprocessing as mp
import struct
import numpy as np
import hid

def shared_to_numpy(mp_arr, nrow, ncol):
    return np.frombuffer(mp_arr.get_obj()).reshape((nrow,ncol))

def worker(remote_buffer_):
    global remote_buffer
    remote_buffer = remote_buffer_
    while True:
        with remote_buffer_.get_lock():
            arr = shared_to_numpy(remote_buffer)
            # get first non-nan row
            bytes_from_dev = d.read(64)
            arr[i] = struct.unpack('>LHH', bytes_from_dev)


nrow = 5
ncol = 11
remote_buffer = mp.Array(ctypes.c_double, nrow*ncol)

arr = shared_to_numpy(remote_buffer, nrow, ncol)
arr[:] = np.nan

p = Process(target=worker, args=(remote_buffer,))

# get the numpy array out as
result = shared_to_numpy(remote_buffer, nrow, ncol)

