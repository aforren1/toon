from multiprocessing import set_start_method, freeze_support

if __name__ == '__main__':
    set_start_method('spawn')
    freeze_support()
    import numpy as np
    from psychopy import core, visual, event, monitors
    from toon.input import BlamBirds, Mouse

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
                           ports=['COM11'])
        win.viewScale = [-1, 1]  # mirror image
    else:
        device = Mouse(win=win)
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

        baseline = None
        while baseline is None:
            baseline = dev.read()[0]
        baseline = np.median(baseline, axis=0)[0:2]
        pointer.pos = baseline

        while not event.getKeys():
            data = dev.read()[0]
            if data is not None:
                newdata = data[-1, 0:2]
                if rotation:
                    newdata2 = newdata
                    newdata[0] = _rotx[0] * newdata2[0] + _rotx[1] * newdata2[1]
                    newdata[1] = _roty[0] * newdata2[0] + _roty[1] * newdata2[1]
                print(newdata)
                pointer.pos = newdata
            win.flip()
