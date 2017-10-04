toon: tools for neuroscience
============================

[![Version](https://img.shields.io/pypi/v/toon.svg)](https://pypi.python.org/pypi/toon)
[![License](https://img.shields.io/pypi/l/toon.svg)](https://raw.githubusercontent.com/aforren1/toon/master/LICENSE.txt)
[![Travis](https://img.shields.io/travis/aforren1/toon.svg)](https://travis-ci.org/aforren1/toon)
[![Coveralls](https://img.shields.io/coveralls/aforren1/toon.svg)](https://coveralls.io/github/aforren1/toon)

Install:

python 2.7, 3.6:

```shell
pip install toon
```

Devel (both):

```shell
pip install git+https://github.com/aforren1/toon
```

Three modules so far: audio, input, and tools.

## Audio

```python
import numpy as np
import toon.audio as ta
from psychopy import sound

beeps = ta.beep_sequence([440, 880, 1220], inter_click_interval=0.4)
beep_aud = sound.Sound(np.transpose(np.vstack((beeps, beeps))), 
                       blockSize=32, 
                       hamming=False)
beep_aud.play()
```

## Input

Input devices include:
 - HAND (custom force measurement device) by class `Hand`
 - Flock of Birds (position tracker) by class `BlamBirds`
 - Keyboard (for changes in keyboard state, more accurate timing) via `Keyboard`
 - DebugKeyboard (for current keyboard state, constant error of up to 9 ms?) via `DebugKeyboard`
 - Force Transducers (predecessor to HAND) by class `ForceTransducers` (Windows only.)
 
Generally, input devices can be used as follows:

```python
from psychopy import core
from toon.input import <device>

timer = core.monotonicClock

dev = <device>(multiprocess=True, clock_source=timer, <device-specific args>)

with dev as d:
    while not done:
        timestamp, data = d.read()
        ...

```

You can perform a sanity check for existing devices via:

```shell
python -m toon.examples.test_inputs --dev <device> --mp True
```

## Tools

Current tools:
 - cart2pol
 - pol2cart
 - cart2sph
 - sph2cart

For example:

```python
import toon.tools as tt

x, y = tt.pol2cart(45, 3, units='deg', ref=(1, 1))
```

## Extended Examples

If you have psychopy and the HAND, you can run an example via:

```python
python -m toon.examples.psychhand
```

If you're hooked up to the kinereach (also works with a mouse), try:

```python
python -m toon.examples.kinereach
```