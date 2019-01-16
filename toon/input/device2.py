import abc
import six
import inspect
from collections import namedtuple

from toon.input.clock import mono_clock
from toon.input.device import Obs


def make_obs(name, shape, ctype):
    return type(name, (Obs,), {'shape': shape, 'ctype': ctype})


def prevent_if_remote(func):
    def wrap_if_remote(*args, **kwargs):
        self = args[0]
        if self._local:
            return func(*args, **kwargs)
        raise ValueError('Device is being used on a remote process.')
    return wrap_if_remote


@six.add_metaclass(abc.ABCMeta)
class BaseDevice():
    sampling_frequency = 500

    def __init__(self, clock=mono_clock.get_time):
        # call *after* any subclass init
        self._local = True  # MpDevice toggles this in the main process
        _obs = self.get_obs()
        self.Returns = self.build_named_tuple(_obs)
        self.clock = clock

    def enter(self):
        pass

    @prevent_if_remote
    def __enter__(self):
        self.enter()
        return self

    def exit(self, *args):
        pass

    @prevent_if_remote
    def __exit__(self, *args):
        self.exit(*args)

    @prevent_if_remote
    def do_read(self):
        intermediate = self.read()
        if isinstance(intermediate, self.Returns):
            return intermediate
        if not (isinstance(intermediate, list) or isinstance(intermediate, tuple)):
            intermediate = [intermediate]
        else:
            intermediate = list(intermediate)
            intermediate.sort(key=lambda x: type(x).__name__)
        return self.Returns(*intermediate)

    @abc.abstractmethod
    def read(self):
        pass

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


class Derived(BaseDevice):
    Pos = make_obs('Pos', (3,), float)
    Ori = make_obs('Ori', (2, 2), int)

    def __init__(self):
        print('inited')
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
        return (self.Pos(2, (1, 2, 3)),
                self.Ori(3, [[1, 2], [3, 4]]))
