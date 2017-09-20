# run as `python -m psychhand.py`

if __name__ == '__main__':
    import numpy as np
    from psychopy import core, visual, event, logging
    from multiprocessing import freeze_support
    freeze_support()

    from toon.input import Hand

    timer = core.monotonicClock

    win = visual.Window(size=(1920, 1080),
                        screen=0,
                        units='height',
                        fullscr=True)
    win.recordFrameIntervals = True
    win.refreshThreshold = 1/60 + 0.004
    logging.console.setLevel(logging.WARNING)
    # make one circle per axis
    rad = 0.05
    opacity = 0.5

    baseline_circles = [visual.Circle(win, fillColor='black',
                                      opacity=1,
                                      autoDraw=True,
                                      lineWidth=3)
                        for i in range(5)]
    colours = ['#34a853', '#4285f4', '#ed1c24', '#fbbc05', '#a5a0a9']
    controlled_circles = [visual.Circle(win, fillColor=colours[i],
                                        opacity=opacity,
                                        autoDraw=True,
                                        radius=rad,
                                        lineWidth=3)
                          for i in range(5)]

    # start device
    dev = Hand(multiprocess=True, clock_source=timer)
    dev.start()
    core.wait(0.5)
    # take a few readings to set baseline
    # wait until we get any data (device takes a few secs to
    # run the calibration routine)
    baseline = None
    while baseline is None:
        baseline = dev.read()[0]
    baseline = np.median(baseline, axis=0)

    j = 1
    factor = 1 # 'visual gain' = scale the raw input so it tends to stay on the screen
    offset = np.linspace(-0.4, 0.4, num=5)
    for i in range(5):
        # we want each to start at (0,0) in relative coordinates,
        # and the radius to be 0.05 (just eyeballing)
        baseline_circles[i].pos = (offset[i], 0)
        baseline_circles[i].radius = 0.05
        controlled_circles[i].pos = baseline_circles[i].pos
        controlled_circles[i].radius = 0.05
        j += 3

    # hit any key to exit
    while not event.getKeys():
        data = dev.read()[0]
        # data returns None if all nans
        if data is not None:
            # print(data)
            # take median of current chunk & subtract off median of calibration
            newdata = np.median(data, axis=0)
            j = 0
            for i in range(5):
                controlled_circles[i].pos = (-newdata[j] / factor + offset[i] + baseline[j]/factor,
                                             (newdata[j+1] / factor) - baseline[j+1]/factor)
                controlled_circles[i].radius = (1/(20 + 100*(newdata[j+2] - baseline[j+2])/factor))
                j += 3

        win.flip()
    dev.close()

    print('Overall, %i frames were dropped.' % win.nDroppedFrames)
