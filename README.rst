toon
====

.. image:: https://img.shields.io/pypi/v/toon.svg
     :target: https://pypi.python.org/pypi/toon

.. image:: https://img.shields.io/pypi/l/toon.svg
     :target: https://raw.githubusercontent.com/aforren1/toon/master/LICENSE.txt

.. image:: https://img.shields.io/travis/aforren1/toon.svg
     :target: https://travis-ci.org/aforren1/toon

.. image:: https://img.shields.io/appveyor/ci/aforren1/toon.svg
     :target: https://ci.appveyor.com/project/aforren1/toon

.. image:: https://img.shields.io/coveralls/aforren1/toon.svg
     :target: https://coveralls.io/github/aforren1/toon

Description
-----------

Additional tools for neuroscience experiments, including:

* A framework for polling input devices on a separate process.
* Helper functions for generating auditory stimuli (read: beeps).
* Coordinate tools (slightly modified from :code:`psychopy.tools.coordinatetools`), which additionally allow for calculations relative to points other than the origin.

Everything *should* work on Windows/Mac/Linux.

See requirements.txt for dependencies.

Many of the full examples require :code:`psychopy` to operate.

Install
-------

Current release::

    pip install toon

Development version::

    pip install git+https://github.com/aforren1/toon

For full install (including dependencies of included devices)::

    pip install toon[full]

See setup.py for a list of those dependencies, as well as device-specific subdivisions.

Usage Overview
--------------

Audio
~~~~~

This module provides simple helper functions for generating beeps and beep seqeuences.

This sample generates a three-beep metronome for the timed response experiment.::

     import numpy as np
     import toon.audio as ta
     from psychopy import sound

     beeps = ta.beep_sequence([440, 880, 1220], inter_click_interval=0.4)
     beep_aud = sound.Sound(np.transpose(np.vstack((beeps, beeps))),
                            blockSize=32,
                            hamming=True)
     beep_aud.play()

Input
~~~~~

This module allows us to sample from external devices on a secondary process at high rates, and efficiently move that data to the main process via the `multiprocessing` module.

Generally useful input devices include:

- Keyboard (for changes in keyboard state) via :code:`Keyboard`
- Mouse (for mouse position) via :code:`Mouse`

The following are in-house devices, which may not be generally useful but could serve as examples
of how to implement additional devices:

- HAND (custom force measurement device) by class :code:`Hand`
- Force Keyboard (predecessor to HAND) by class :code:`ForceKeyboard` (Windows only, due to :code:`nidaqmx` requirement.)

Generally, input devices can be used as follows::

     from psychopy import core
     from toon.input import <device>, MultiprocessInput

     timer = core.monotonicClock.getTime

     dev = MultiprocessInput(<device>, clock=timer, <device-specific kwargs>)

     dev.start()
     while not done:
         time, data = dev.read()
         ...
     dev.stop()


See `demos/try_input.py <https://github.com/aforren1/toon/blob/master/demos/try_input.py>`_ for usage examples (not packaged).

Tools
~~~~

These tools are extensions of the ones provided in :code:`psychopy.tools.coordinatetools`, allowing for conversion between cartesian<->polar coordinates when the reference point is not (0, 0) in cartesian space.

Current tools:

- :code:`cart2pol`
- :code:`pol2cart`
- :code:`cart2sph`
- :code:`sph2cart`

For example,::

    import toon.tools as tt

    x, y = tt.pol2cart(45, 3, units='deg', ref=(1, 1))

