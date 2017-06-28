import abc
from time import time

class InputBase(object):
    """Base class for inputs
    e.g.
    from psychopy import core
    input = FlockOfBirds(clock_source=core.getTime)
    """
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def __init__(self, clock_source=None):
        self.clock = time if not clock_source else clock_source
    
    @abc.abstractmethod
    def start(self):
        """Start acquiring/recording from the device."""
        return
    
    @abc.abstractmethod
    def stop(self):
        """Stop acquiring/recording from the device."""
        return
    
    @abc.abstractmethod
    def close(self):
        """Close"""
        return
    
    @abc.abstractmethod
    def read(self):
        """Read data from the input source and clear buffer"""
        return self._raw_to_exp(self._world_to_raw())
    
    @abc.abstractmethod
    def write(self, data):
        """Write data to the input source"""
        return
    
    @abc.abstractmethod
    def clear(self):
        """Clear any buffered input"""
        return
    
    @abc.abstractmethod
    def _world_to_raw(self):
        """Take input from the world (defined once per device)"""
        return
    @abc.abstractmethod
    def _raw_to_exp(self, values):
        """Convert raw data to experiment-specific (defined once per experiment)"""
        return values
    