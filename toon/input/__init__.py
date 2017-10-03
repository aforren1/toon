"""Input devices.
.. moduleauthor:: Alexander Forrence <aforren1@jhu.edu>
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from platform import system

from future import standard_library
standard_library.install_aliases()
from .base_input import BaseInput, DummyTime
from .hand import Hand
from .birds import BlamBirds
from .keyboard import Keyboard, DebugKeyboard
if system() is 'Windows':
    from .force_transducers import ForceTransducers
