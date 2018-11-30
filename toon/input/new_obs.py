import numpy as np

# tons of thanks to
# https://stackoverflow.com/questions/31282764/when-subclassing-a-numpy-ndarray-how-can-i-modify-getitem-properly
# and https://docs.scipy.org/doc/numpy/user/basics.subclassing.html

# copy, empty_like, etc. don't *quite* get the timestamp right
# they only get the last element AFAIK


class Obs(np.ndarray):
    def __new__(cls, data, time=None):
        obj = np.asarray(data).view(cls)
        obj.time = np.asarray(time)
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.time = getattr(obj, 'time', None)
        try:
            self.time = self.time[obj._new_time_index]
        except:
            pass

    def __getitem__(self, item):
        try:
            self._new_time_index = item
        except:
            pass
        return super().__getitem__(item)


if __name__ == '__main__':
    xx = Obs([[3], [2], [3]], time=[0.1, 0.2, 0.3])
    yy = Obs([1., 3.14, 2], time=1.2)
