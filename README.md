toon: tools for neuroscience
============================

[![Version](https://img.shields.io/pypi/v/toon.svg)]()
[![License](https://img.shields.io/pypi/l/toon.svg)]()
[![Travis](https://img.shields.io/travis/aforren1/toon.svg)]()


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

Usage (incomplete):

```python
import toon.audio as ta
import toon.input as ti
import toon.tools as tt

beeps = ta.beep_train(click_freq=[440, 660, 880],
                      num_clicks=3)
x, y = tt.pol2cart(45, 3, units='deg', ref=(1, 1))

hand = ti.Hand()
```
