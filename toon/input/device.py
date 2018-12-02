import abc
import six
from collections import namedtuple
import numpy as np
from toon.input.clock import mono_clock
import inspect
import ctypes


@six.add_metaclass(abc.ABCMeta)
class Obs():
    @property
    @abc.abstractmethod
    def shape(self):
        return None

    @property
    @abc.abstractmethod
    def ctype(self):
        return None
    # single observation

    def __init__(self, time, data):
        try:
            self.time = float(time)  # what if time is not a double?
            # is reshape expensive? should we just trust they did it right?
            self.data = np.asarray(data, dtype=self.ctype)
            self.data.shape = self.shape  # will error if mismatch?
        except (TypeError, ValueError):  # time or data not right
            self.time = None
            self.data = None

    def __repr__(self):
        return 'type: %s\ntime: %f\ndata: %s\nshape: %s\nctype: %s' % (type(self).__name__, self.time, self.data, self.shape, self.ctype)

    def __str__(self):
        return '%s(time: %f, data: %s)' % (type(self).__name__, self.time, self.data)

    def any(self):
        return not (self.time is None or self.data is None)


@six.add_metaclass(abc.ABCMeta)
class BaseDevice():
    def __init__(self, clock=mono_clock.get_time, **kwargs):
        _obs = self.__class__.get_obs()
        self.Returns = BaseDevice.build_named_tuple(_obs)
        self.clock = clock

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self):
        pass

    sampling_frequency = 500

    # helpers to figure out the data returned by device
    # (without instantiation--key b/c we need to do *before* we instantiate on other process)
    @classmethod
    def get_obs(cls):
        # get all user-defined Obs defined within the class (as long as they don't start w/ double underscore)
        # separated from tuple building so that
        return [getattr(cls, p) for p in dir(cls) if not p.startswith('__')
                and not p.startswith('_abc')
                and not isinstance(getattr(cls, p), property)
                and inspect.isclass(getattr(cls, p))
                and issubclass(getattr(cls, p), Obs)]

    @classmethod
    def build_named_tuple(cls, obs):
        if obs:
            class Returns(namedtuple('Returns', [x.__name__.lower() for x in obs])):
                def any(self):
                    # simplify user checking of whether there's any data
                    return any([x is not None and x.time is not None for x in self])
            # default values of namedtuple to None (see mouse.py for example why)
            Returns.__new__.__defaults__ = (None,) * len(Returns._fields)
            return Returns
        return None
