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
        data_dims = check_and_fix_dims(self.device.data_shapes(**self.device_args))
        self.not_time_axis = [tuple(range(-1, -(len(dd) + 1), -1)) for dd in data_dims]  # TODO: unclear, change later
        # if not manually overridden, preallocate 10*sampling freq
        nrow = self.nrow
        if not nrow:
            nrow = int((self.device.samp_freq(**self.device_args) * 10)/60)

        # preallocate data arrays (shared arrays, numpy equivalents, and local copies)
        data_types = self.device.data_types(**self.device_args)
        self.mp_data_arrays = []
        self.np_data_arrays = []
        self.local_data_arrays = []
        for counter, data_dim in enumerate(data_dims):
            data_dim.insert(0, nrow)  # make axis 0 time
            prod = int(np.prod(data_dim))
            data_type = data_types[counter]
            self.mp_data_arrays.append(mp.Array(data_type,
                                                prod,
                                                lock=self.shared_lock))
            self.np_data_arrays.append(shared_to_numpy(self.mp_data_arrays[counter], data_dim, data_type))
            self.np_data_arrays[counter].fill(np.nan)
            self.local_data_arrays.append(np.copy(self.np_data_arrays[counter]))

        # preallocate time array
        self.mp_time_array = mp.Array(ctypes.c_double, nrow, lock=self.shared_lock)
        self.np_time_array = shared_to_numpy(self.mp_time_array, nrow, ctypes.c_double)
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
                                        nrow, data_dims, data_types))
        self.process.daemon = True
        self.process.start()
        self.remote_ready.wait()
        return self

    def read(self):
        with self.shared_lock:
            np.copyto(self.local_time_array, self.np_time_array)
            for local_data, remote_data in zip(self.local_data_arrays, self.np_data_arrays):
                np.copyto(local_data, remote_data)
            self.np_time_array.fill(np.nan)
            for i in self.np_data_arrays:
                i.fill(np.nan)
        if np.isnan(self.local_time_array).all():
            return None, None
        dims = self.not_time_axis
        time = self.local_time_array[~np.isnan(self.local_time_array)]
        if len(dims) == 1:
            data = self.local_data_arrays[0][~np.isnan(self.local_data_arrays[0]).any(axis=dims[0])]
        else:
            data = [local_data[~np.isnan(local_data).any(axis=dim)] for
                    local_data, dim in zip(self.local_data_arrays, dims)]
        return time, data


    @staticmethod
    def worker(device, device_args, shared_lock, remote_ready, kill_remote, mp_time_array, mp_data_arrays,
               nrow, data_dims, data_types):
        dev = device(**device_args)
        np_time_array = shared_to_numpy(mp_time_array, nrow, ctypes.c_double)
        np_time_array.fill(np.nan)
        np_data_arrays = []
        for data, dims, types in zip(mp_data_arrays, data_dims, data_types):
            np_data_arrays.append(shared_to_numpy(data, dims, types))
        for i in np_data_arrays:
            i.fill(np.nan)
        with dev as d:
            remote_ready.set()
            while not kill_remote.is_set():
                timestamp, data = d.read()
                if timestamp is not None:
                    with shared_lock:
                        current_nans = np.isnan(np_time_array)
                        if current_nans.any():  # nans to fill in
                            next_index = np.where(current_nans)[0][0]
                            if isinstance(data, list):
                                for np_data, new_data in zip(np_data_arrays, data):
                                    np_data[next_index, :] = new_data
                            else:
                                np_data_arrays[0][next_index, :] = data
                            np_time_array[next_index] = timestamp
                        else: # replace oldest data with newest data
                            if isinstance(data, list):
                                for np_data, new_data in zip(np_data_arrays, data):
                                    np_data[:] = np.roll(np_data, -1, axis=0)
                                    np_data[-1, :] = new_data
                            else:
                                np_data_arrays[0][:] = np.roll(np_data_arrays[0], -1, axis=0)
                                np_data_arrays[0][-1, :] = data
                            np_time_array[:] = np.roll(np_time_array, -1, axis=0)
                            np_time_array[-1] = timestamp

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.kill_remote.set()
