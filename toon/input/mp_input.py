import multiprocessing as mp
import ctypes
import numpy as np
from toon.input.helper import check_and_fix_dims, shared_to_numpy

class MultiprocessInput(object):
    def __init__(self, device=None, nrow=None, **kwargs):
        """_nrow overrides default size (10*sampling_frequency)"""
        self.device = device
        self.device_args = kwargs
        self.nrow = nrow

    def __enter__(self):
        self.shared_lock = mp.Lock()
        self.remote_ready = mp.Event()
        self.kill_remote = mp.Event()
        data_dims = check_and_fix_dims(self.device.data_shapes(self.device_args))
        # if not manually overridden, preallocate 10*sampling freq
        nrow = self.nrow
        if not nrow:
            nrow = self.device.samp_freq(self.device_args) * 10

        # preallocate data arrays (shared arrays, numpy equivalents, and local copies)
        data_types = self.device.data_types(self.device_args)
        self.mp_data_arrays = []
        self.np_data_arrays = []
        self.local_data_arrays = []
        for counter, data_dim in enumerate(data_dims):
            data_dim.insert(0, nrow)  # make axis 0 time
            data_type = data_types[counter]
            self.mp_data_arrays.append(mp.Array(data_type,
                                                int(np.prod(data_dim)),
                                                lock=self.shared_lock))
            self.np_data_arrays.append(shared_to_numpy(self.mp_data_arrays[counter], data_dim))
            self.np_data_arrays[counter].fill(np.nan)
            self.local_data_arrays.append(np.copy(self.np_data_arrays[counter]))

        # preallocate time array
        self.mp_time_array = mp.Array(ctypes.c_double, nrow, lock=self.shared_lock)
        self.np_time_array = shared_to_numpy(self.mp_time_array, nrow)
        self.np_time_array.fill(np.nan)
        self.local_time_array = np.copy(self.np_time_array)

        #
        self.process = mp.Process(target=self.worker,
                                  args=(self.device,
                                        self.device_args,
                                        self.shared_lock,
                                        self.remote_ready,
                                        self.kill_remote,
                                        self.mp_time_array,
                                        self.mp_data_arrays,
                                        nrow, data_dims))
        self.process.daemon = True
        self.process.start()
        self.remote_ready.wait()

    def read(self):


    @staticmethod
    def worker(device, device_args, shared_lock, remote_ready, kill_remote, mp_time_array, mp_data_arrays,
               nrow, data_dims):
        dev = device(device_args)
        np_time_array = shared_to_numpy(mp_time_array, nrow)
        np_data_arrays = []
        for counter, arr in enumerate(mp_data_arrays):
            np_data_arrays.append(shared_to_numpy(arr, data_dims[counter]))
        with dev as d:
            remote_ready.set()
            while not kill_remote.is_set():
                timestamp, data = d.read()
                if timestamp is not None:
                    with shared_lock:
                        if isinstance(timestamp, list):
                            # special handling for when there's more than one datapoint per read
                            # can just iterate through the list and do the usual
                            pass
                        else:
                            current_nans = np.isnan(np_time_array).any(axis=1)
                            if current_nans.any():
                                next_index = np.where(current_nans)[0][0]


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.kill_remote.set()

    def clear_shared_arrays(self):
        self.np_time_array.fill(np.nan)
        for i in self.np_data_arrays:
            i.fill(np.nan)


