import abc
import six
import inspect
import numpy as np
from collections import namedtuple

from toon.input.clock import mono_clock


def make_obs(name, shape, ctype):
    """Helper function to make subclasses of Obs."""
    return type(name, (Obs,), {'shape': shape, 'ctype': ctype})


def prevent_if_remote(func):
    """Decorator to raise ValueError in order to prevent accidental use
    of a remote device locally.
    """
    def wrap_if_remote(*args, **kwargs):
        self = args[0]
        if self._local:
            return func(*args, **kwargs)
        raise ValueError('Device is being used on a remote process.')
    return wrap_if_remote


@six.add_metaclass(abc.ABCMeta)
class Obs():
    """Abstract base class for observations.

    This is subclassed when making new subclasses of toon.input.BaseDevice,
    and is used to preallocate shared memory between the device and main processes.
    """
    @property
    @abc.abstractmethod
    def shape(self):
        """Shape of the observation."""
        return None

    @property
    @abc.abstractmethod
    def ctype(self):
        """Data type of the observation. Can be built-in type (e.g. int, float),
        numpy types, or ctypes types.
        """
        return None

    def __init__(self, time, data):
        """Create a new Observation.

        Parameters
        ----------
        time: float
            Time that the data was observed.
        data: array_like
            Observed data. Must match the shape of the subclass.
        """
        self.time = float(time)  # what if time is not a double?
        # is reshape expensive? should we just trust they did it right?
        self.data = np.asarray(data, dtype=self.ctype)
        self.data.shape = self.shape  # will error if mismatch?

    def __repr__(self):
        return 'type: %s\ntime: %f\ndata: %s\nshape: %s\nctype: %s' % (type(self).__name__, self.time, self.data, self.shape, self.ctype)

    def __str__(self):
        return '%s(time: %f, data: %s)' % (type(self).__name__, self.time, self.data)


@six.add_metaclass(abc.ABCMeta)
class BaseDevice():
    """Abstract base class for input devices.
    Attributes
    ----------
    sampling_frequency: int
        Expected sampling frequency of the device, used by toon.input.MpDevice for preallocation.
        We preallocate for 1 second of data (e.g. 500 samples for a sampling_frequency of 500 Hz).

    Notes
    -----
    The user supplies `enter` and `exit`, not the dunder methods (`__enter__`, `__exit__`).
    """
    sampling_frequency = 500

    def __init__(self, clock=mono_clock.get_time):
        """Create new device.
        Parameters
        ----------
        clock: function or method
            The clock used for timestamping events. Defaults to toon.input.mono_clock, which
            allows us to share a reference time between the parent and child processes. The 
            mono_clock is based off psychopy.clock.MonotonicClock 
            (on Windows, time.perf_counter seems to be relative to when the process is created, 
            which makes it difficult to relate the time between processes).

        Notes
        -----
        Make sure to call this `__init__` in subclasses *after* the `__init__` from the subclass.

        Do not start communicating with the device in `__init__`, wait until `enter()`.

        """
        # call *after* any subclass init
        self._local = True  # MpDevice toggles this in the main process
        _obs = self.get_obs()
        self.Returns = self.build_named_tuple(_obs)
        self.clock = clock

    def enter(self):
        pass

    @abc.abstractmethod
    def read(self):
        pass

    def exit(self, *args):
        pass

    @prevent_if_remote
    def __enter__(self):
        self.enter()
        return self

    @prevent_if_remote
    def __exit__(self, *args):
        self.exit(*args)

    @prevent_if_remote
    def do_read(self):
        intermediate = self.read()
        # user provided a self.Returns() already, short-circuit
        if isinstance(intermediate, self.Returns):
            return intermediate
        # single Obs, but we'll squeeze it into the same framework as multi-Obs
        if not (isinstance(intermediate, list) or isinstance(intermediate, tuple)):
            intermediate = [intermediate]
        # tuple or list (hopefully), listify
        else:
            # list of Returns
            if isinstance(intermediate[0], self.Returns):
                return intermediate
            intermediate = list(intermediate)
            intermediate.sort(key=lambda x: type(x).__name__)
        return self.Returns(*intermediate)

    @property
    def local(self):
        return self._local

    @local.setter
    def local(self, val):
        self._local = bool(val)

    # helpers to figure out the data returned by device
    # (without instantiation--key b/c we need to do *before* we instantiate on other process)
    def get_obs(self):
        # get all user-defined Obs defined within the class (as long as they don't start w/ double underscore)
        # separated from tuple building so that
        return [getattr(self, p) for p in dir(self) if not p.startswith('__')
                and not p.startswith('_abc')
                and not isinstance(getattr(self, p), property)
                and inspect.isclass(getattr(self, p))
                and issubclass(getattr(self, p), Obs)]

    def build_named_tuple(self, obs):
        if obs:
            class Returns(namedtuple('Returns', [x.__name__.lower() for x in obs])):
                def any(self):
                    # simplify user checking of whether there's any data
                    return any([x is not None for x in self])
            # default values of namedtuple to None (see mouse.py for example why)
            Returns.__new__.__defaults__ = (None,) * len(Returns._fields)
            return Returns
        return None


# out
Pos = make_obs('Pos', (3,), float)


class Derived(BaseDevice):
    # these can be defined outside the scope
    Pos = Pos
    Ori = make_obs('Ori', (2, 2), int)

    def __init__(self):
        print('inited')
        # runtime Obs
        self.Scale = make_obs('Scale', (1,), float)
        super(Derived, self).__init__()

    def enter(self):
        print('entered')

    def exit(self, *args):
        print('exited')

    def read(self):
        # either
        # a. return data without stuffing into self.Returns,
        #      which means we do it later in do_read
        # b. stuff into self.Returns (necessary if potentially missing data),
        #      e.g. current Mouse
        print('readed')
        return (Pos(2, (1, 2, 3)),
                self.Scale(1, 2.2),
                self.Ori(3, [[1, 2], [3, 4]]))
