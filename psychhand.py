# run as `python -m psychhand.py`
# middle finger only
import numpy as np
from input.hand import Hand
from psychopy import core, visual, event

timer = core.monotonicClock

win = visual.Window(size=(600, 600),
                    screen=0,
                    units='height')
# make one circle per axis
rad = 0.05
opacity = 0.5
xcircle = visual.Circle(win, radius=rad,
                        fillColor='darkorchid',
                        opacity=opacity,
                        pos=(-.25, 0),
                        autoDraw=True)

ycircle = visual.Circle(win, radius=rad,
                        fillColor='green',
                        opacity=opacity,
                        pos=(0, 0),
                        autoDraw=True)

zcircle = visual.Circle(win, radius=rad,
                        fillColor='lightcoral',
                        opacity=opacity,
                        pos=(0.25, 0),
                        autoDraw=True)
# start device
dev = Hand(multiproc=True, time=timer)
dev.start()
core.wait(0.5)
# take a few readings to set baseline
baseline = dev.read()
baseline = np.median(baseline[:, 2:], axis=0)

while not event.getKeys():
    data = dev.read()
    # data returns None if all nans
    if data is not None:
        #print(data)
        # take median of current chunk & subtract off median of calibration
        newdata = np.median(data[:, 2:], axis=0)
        xcircle.pos = (-0.25, newdata[6] - baseline[6])
        ycircle.pos = (0, newdata[7] - baseline[7])
        zcircle.pos = (0.25, newdata[8] - baseline[8])
    win.flip()
dev.close()

