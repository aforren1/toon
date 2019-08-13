import numpy as np
from psychopy import visual, core, event, logging

from toon.input import MpDevice, mono_clock, stack
from toon.input.mouse import Mouse

# relate toon time to psychopy time
# conversely, feed in psychopy's clock.monotonicClock.getTime
# as an argument to MpDevice
logging.setDefaultClock(mono_clock)

win = visual.Window(fullscr=True, units='pix')

psy_mouse = event.Mouse()
toon_mouse = MpDevice(Mouse())

psy_cir = visual.Circle(win, size=100, fillColor='red', opacity=0.5, lineColor=None)
toon_cir = visual.Circle(win, size=100, fillColor='blue', opacity=0.5, lineColor=None)
toon_cir.pos = (-win.size[0]/2, win.size[1]/2)
data_list = []

with toon_mouse:  # alternatively, use toon_mouse.start(), toon_mouse.stop()
    while not event.getKeys(['esc', 'escape']):
        clicks, pos, scroll = toon_mouse.read()
        if pos is not None:
            data_list.append(pos.copy())
            pos *= [1, -1]
            for i in pos:
                toon_cir.pos += i
        psy_cir.pos = psy_mouse.getPos()
        psy_cir.draw()
        toon_cir.draw()
        win.flip()

win.close()
data_stack = stack(data_list)
print(data_stack)
print(np.diff(data_stack.time))

core.quit()
