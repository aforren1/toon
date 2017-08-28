toon: tools for neuroscience
============================

Install:

(This is somewhat temporary, until the pip-enhanced version of psychopy hits pypi)

python 2.7, 3.6:

pip install toon


Devel (both):

pip install git+https://github.com/aforren1/toon


Three modules so far: audio, input, and tools.

Usage (incomplete):

import toon.audio as ta
import toon.input as ti
import toon.tools as tt

beeps = ta.beep_train(click_freq=[440, 660, 880],
                      num_clicks=3)
x, y = tt.pol2cart(45, 3, units='deg', ref=(1, 1))

hand = ti.Hand()
