from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from future import standard_library

standard_library.install_aliases()
from multiprocessing import set_start_method, freeze_support
import os

not_travis = 'TRAVIS' not in os.environ
if not_travis:
    from psychopy import event


    class MouseWrapper(object):
        def __init__(self):
            self.mouse = event.Mouse(visible=True)

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            pass

        def read(self):
            return self.mouse.getPos()

if __name__ == '__main__':
    set_start_method('spawn')
    freeze_support()
    import numpy as np
    from psychopy import core, visual, monitors
    from toon.input import BlamBirds

    flock = False
    rotation = True
    mon = monitors.Monitor('tmp')
    mon.setSizePix((1280, 720))
    mon.setWidth(121)
    win = visual.Window(size=(1280, 720), fullscr=True,
                        screen=1, monitor=mon, units='cm',
                        allowGUI=False)

    if flock:
        device = BlamBirds(multiprocess=True, master='COM11',
                           ports=['COM10', 'COM11', 'COM12', 'COM13'],
                           sample_ports=['COM10', 'COM12'])
        win.viewScale = [-1, 1]  # mirror image
    else:
        device = MouseWrapper()
    core.wait(1)

    _rotx = (1, 0)
    _roty = (0, 1)
    if rotation:
        _theta = 30
        _rad = _theta * np.pi / 180.0
        _rotx = (np.cos(_rad), np.sin(_rad))
        _roty = (-np.sin(_rad), np.cos(_rad))

    with device as dev:
        center = visual.Circle(win, radius=2, fillColor='green', pos=(0, 0),
                               autoDraw=True)

        pointer = visual.Circle(win, radius=2.54 / 2, fillColor='darkmagenta',
                                pos=(0, 0), autoDraw=True)

        pointer_actual = visual.Circle(win, radius=2.54 / 2, fillColor='magenta',
                                       pos=(0, 0), autoDraw=True, opacity=0.6)

        if flock:
            baseline = None
            while baseline is None:
                baseline = dev.read()[1]
            baseline = np.median(baseline, axis=0)[0:2]
            pointer.pos = baseline
        else:
            baseline = dev.read()

        while not event.getKeys():
            if flock:
                data = dev.read()[1]
                if data is not None:
                    data = data[-1, 0:2]
            else:
                data = device.read()
            if data is not None:
                pointer_actual.pos = data
                if rotation:
                    data2 = data
                    data[0] = _rotx[0] * data2[0] + _rotx[1] * data2[1]
                    data[1] = _roty[0] * data2[0] + _roty[1] * data2[1]
                print(data)
                pointer.pos = data
            win.flip()
