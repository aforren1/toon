import numpy as np
from ctypes import c_double
# tons of thanks to
# https://stackoverflow.com/questions/31282764/when-subclassing-a-numpy-ndarray-how-can-i-modify-getitem-properly
# and https://docs.scipy.org/doc/numpy/user/basics.subclassing.html


class TsArray(np.ndarray):
    def __new__(cls, data, time=None):
        obj = np.asarray(data).view(cls)
        obj.time = np.asarray(time, dtype=c_double)
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.time = getattr(obj, 'time', None)
        try:
            self.time = self.time[obj._new_time_index]
        except:
            pass

    def copy(self, **kwargs):
        self._new_time_index = slice(None, None, None)
        return super(TsArray, self).copy(**kwargs)

    def __getitem__(self, item):
        try:
            if isinstance(item, (slice, int)):
                self._new_time_index = item
            else:
                self._new_time_index = item[0]
        except:
            pass
        return super(TsArray, self).__getitem__(item)
