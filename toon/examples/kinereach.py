from multiprocessing import set_start_method, freeze_support

if __name__ == '__main__':
    set_start_method('spawn')
    freeze_support()
    import numpy as np
    from psychopy import core, visual, event, monitors
    from toon.input import BlamBirds, Mouse

    flock=False
    mon = monitors.Monitor('tmp')
    mon.setSizePix((1280, 720))
    mon.setWidth(121)
    win = visual.Window(size=(1280, 720), fullscr=True,
                        screen=1, monitor=mon, units='cm',
                        allowGUI=False)


    if flock:
        device = BlamBirds(multiprocess=True, master='/dev/ttyUSB0',
                           ports=['/dev/ttyUSB0', '/dev/ttyUSB1'])
        win.viewScale = [-1, 1]  # mirror image
    else:
        device = Mouse(win=win)
    core.wait(1)

    with device as dev:
        center = visual.Circle(win, radius=2, fillColor='green', pos=(0, 0),
                               autoDraw=True)

        pointer = visual.Circle(win, radius=2.54/2, fillColor='darkmagenta',
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
                print(newdata)
                pointer.pos = newdata
            win.flip()
