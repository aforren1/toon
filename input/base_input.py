import abc
from time import time

def default_raw_to_exp(self, value):
    return value

class BaseInput(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, clock_source=None, 
                 raw_to_exp=default_raw_to_exp, **kwargs):
        self.time = time if not clock_source else clock_source
        self._raw_to_exp = raw_to_exp.__get__(self)
        self._start_time = None
    
    @abc.abstractmethod
    def start(self):
        self._start_time = self.time()
    
    @abc.abstractmethod
    def stop(self):
        return

    @abc.abstractmethod
    def read(self):
        return self._raw_to_exp(self._world_to_raw())

    @abc.abstractmethod
    def _world_to_raw(self):
        return

    @property
    def raw_to_exp(self):
        return self._raw_to_exp

    @raw_to_exp.setter
    def raw_to_exp(self, function):
        self._raw_to_exp = function.__get__(self)
    
    @abc.abstractmethod
    def clear(self):
        return

    


