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
import toon.audio as ta
from psychopy import sound

beeps = ta.beep_sequence([440, 880, 1220], inter_click_interval=0.4)
beep_aud = sound.Sound(beeps, blockSize=32, hamming=False)
beep_aud.play()
```

## Input

Flock of Birds:

```python
import time
from toon.input import BlamBirds

dev = BlamBirds(multiprocess=True)
dev.start()

for ii in range(50):
    print(dev.read())
    time.sleep(0.166)

dev.close()
```

## Tools

```python
import toon.tools as tt

x, y = tt.pol2cart(45, 3, units='deg', ref=(1, 1))
```

## Extended Examples

If you have psychopy and the HAND, you can run an example via:

```python
python -m toon.examples.psychhand
```
