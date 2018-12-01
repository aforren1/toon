import numpy as np
from ctypes import c_double
# tons of thanks to
# https://stackoverflow.com/questions/31282764/when-subclassing-a-numpy-ndarray-how-can-i-modify-getitem-properly
# and https://docs.scipy.org/doc/numpy/user/basics.subclassing.html


class TsArray(np.ndarray):
    def __new__(cls, data, time=None):
        obj = np.asarray(data).view(cls)
        obj.time = np.asarray(time, dtype=c_double)
        obj._new_time_index = slice(None, None, None)
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.time = getattr(obj, 'time', None)
        try:
            self.time = self.time[obj._new_time_index]
        except:
            pass

    def copy(self):
        self._new_time_index = slice(None, None, None)
        return super(TsArray, self).copy()

    def __getitem__(self, item):
        try:
            if isinstance(item, (slice, int)):
                self._new_time_index = item
            else:
                self._new_time_index = item[0]
        except:
            pass
        return super(TsArray, self).__getitem__(item)


def empty(shape, dtype=float, order='C'):
    return Obs(np.empty(shape, dtype=dtype), empty=True)


if __name__ == '__main__':
    Obs = TsArray
    xx = Obs([[3], [2], [3]], time=[0.1, 0.2, 0.3])
    yy = Obs([1., 3.14, 2], time=1.2)
    zz = xx[:2].copy()  # np.copy(arr) loses the time attribute
    zz == xx[:2]
    zz.time == xx[:2].time
    tt = Obs([[1, 2, 3], [4, 5, 6], [7, 9, 10], [12, 1, 12]], time=[0.1, 0.2, 0.3, 0.4])