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
* A framework for animating elements.

Everything *should* work on Windows/Mac/Linux.

See requirements.txt for dependencies.

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

Input
~~~~~

This module allows us to sample from external devices on a secondary process at high rates, and efficiently move that data to the main process via the `multiprocessing` module.

Generally useful input devices include:

- Keyboard (for changes in keyboard state) via :code:`Keyboard`
- Mouse (for mouse position) via :code:`Mouse`

The following are in-house devices, which may not be generally useful but could serve as examples
of how to implement additional devices:

- HAND (custom force measurement device using hidapi) via :code:`Hand` (for pyusb example, see :code:`USBHand`)
- Force Keyboard (predecessor to HAND) via :code:`ForceKeyboard` (Windows only, due to :code:`nidaqmx` requirement.)
- Flock of Birds (the 1992 vintage from Ascension) via :code:`Birds` (very specific to the KineReach setup in the BLAM Lab)

Generally, input devices can be used as follows::

     from toon.input.mpdevice import MpDevice
     import <device>

     dev = MpDevice(<device>, <device-specific kwargs>)

     with dev:
         while not done:
             data = dev.read()
             if data.any():
                 pass # do something with the data
             ...


See the `demos/ <https://github.com/aforren1/toon/blob/master/demos>`_ folder or snippets in the source of individual devices for usage examples.

Animation
~~~~~~~~~

See the `demos/ <https://github.com/aforren1/toon/blob/master/demos>`_ folder.
