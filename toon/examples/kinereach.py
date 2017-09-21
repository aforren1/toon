from multiprocessing import set_start_method, freeze_support
set_start_method('spawn')
freeze_support()

if __name__ == '__main__':
    import numpy as np
    from psychopy import core, visual, event, monitors, logging
    from toon.input import BlamBirds

    mon = monitors.Monitor('tmp')
    mon.setSizePix((1920, 1080))
    mon.setWidth(68)
    win = visual.Window(size=(1920, 1080), fullscr=True,
                        screen=1, monitor=mon, units='cm',
                        allowGUI=False)

    win.viewScale = [-1, 1] # mirror image
    win.recordFrameIntervals = True
    win.refreshThreshold = 1/60 + 0.004
    logging.console.setLevel(logging.WARNING)

    dev = BlamBirds(multiprocess=True)
    dev.start()
    core.wait(0.5)

    pointer = visual.Circle(win, radius=2.54/2, fillColor='darkmagenta',
                            pos=(0, 0))

    center = visual.Circle(win, radius=2, fillColor='green', pos=(0, 0))

    baseline = None
    while baseline is None:
        baseline, time = dev.read()[0]
    baseline = np.median(baseline, axis=0)[0:2]

    pointer.pos = baseline

    while not event.getKeys():
        data = dev.read()[0]
        if data is not None:
            newdata = np.median(data, axis=0)
            print(newdata)
            pointer.pos = newdata

        win.flip()
    dev.close()

    print('Overall, %i frames were dropped.' % win.nDroppedFrames)

