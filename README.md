toon
====

[![image](https://img.shields.io/pypi/v/toon.svg)](https://pypi.python.org/pypi/toon)
[![image](https://img.shields.io/pypi/l/toon.svg)](https://raw.githubusercontent.com/aforren1/toon/master/LICENSE.txt)
[![image](https://img.shields.io/travis/aforren1/toon.svg)](https://travis-ci.org/aforren1/toon)
[![image](https://img.shields.io/appveyor/ci/aforren1/toon.svg)](https://ci.appveyor.com/project/aforren1/toon)
[![image](https://img.shields.io/coveralls/aforren1/toon.svg)](https://coveralls.io/github/aforren1/toon)

Description
-----------

Additional tools for neuroscience experiments, including:

-   A framework for polling input devices on a separate process.
-   A framework for animating elements.

Everything *should* work on Windows/Mac/Linux.

See requirements.txt for dependencies.

Install
-------

Current release:

```pip install toon```

Development version:

```pip install git+https://github.com/aforren1/toon```

For full install (including dependencies of included devices):

```pip install toon[full]```

See setup.py for a list of those dependencies, as well as
device-specific subdivisions.

Usage Overview
--------------

### Input

This module allows us to sample from external devices on a secondary
process at high rates, and efficiently move that data to the main
process via the multiprocessing module.

Generally useful input devices include:

-   Keyboard (for changes in keyboard state) via `Keyboard`
-   Mouse (for mouse position) via `Mouse`

The following are in-house devices, which may not be generally useful
but could serve as examples of how to implement additional devices:

-   HAND (custom force measurement device using hidapi) via
    `Hand` (for pyusb example, see `USBHand`)
-   Force Keyboard (predecessor to HAND) via
    `ForceKeyboard` (Windows only, due to
    `nidaqmx` requirement.)
-   Flock of Birds (the 1992 vintage from Ascension) via
    `Birds` (very specific to the KineReach setup in the
    BLAM Lab)
-   CyberGlove I (I think? Immersion Corp. branding) via `Cyberglove`

Generally, input devices can be used as follows:

```python
from toon.input import MpDevice
import <device>

dev = MpDevice(<device>, <device-specific kwargs>)

with dev:
    while not done:
        data = dev.read()
        if data.any():
            pass # do something with the data
        ...
```
See the [demos/](https://github.com/aforren1/toon/blob/master/demos)
folder or snippets in the source of individual devices for usage
examples.

### Animation

The `anim` module was derived from [Magnum](https://github.com/mosra/magnum) (though I currently don't implement as many features). See [here](https://doc.magnum.graphics/magnum/classMagnum_1_1Animation_1_1Player.html) for background.

A quick example:

```python
from time import sleep
from toon.anim import Player
from toon.anim import Track
from toon.anim import Timeline
from toon.anim.easing import elastic_in

class Circle(object):
    x = 0
    y = 0

circle = Circle()
keyframes = [(0, 0), (0.5, 0.8), (1.0, 1.0)]
track = Track(keyframes, easing=elastic_in)
player = Player()
player.add('x', track, 'x', circle)

timeline = Timeline()
timeline.start()
player.start(timeline.frame_time)

while timeline.frame_time < 2:
    timeline.next_frame()
    player.update(timeline.frame_time)
    print(circle.x)
    # flip window
    sleep(0.016)

```

See the [demos/](https://github.com/aforren1/toon/blob/master/demos)
folder for a more thorough example including integration with psychopy.
