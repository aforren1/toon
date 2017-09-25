"""Tools to generate audio stimuli.
.. moduleauthor:: Alexander Forrence <aforren1@jhu.edu>
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from .beep_sequence import beep, beep_ramp, beep_sequence
