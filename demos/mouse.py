
from psychopy import visual, core, event

from toon.input.mpdevice import MpDevice
from toon.input.mouse import Mouse

win = visual.Window(fullscr=True, units='pix',
                    waitBlanking=False, multiSample=True,
                    numSamples=8)

psy_mouse = event.Mouse()
toon_mouse = MpDevice(Mouse)

psy_cir = visual.Circle(win, size=100, fillColor='red', opacity=0.5, lineColor=None)
toon_cir = visual.Circle(win, size=100, fillColor='blue', opacity=0.5, lineColor=None)
toon_cir.pos = (-1920/2, 1080/2)
with toon_mouse:  # alternatively, use toon_mouse.start(), toon_mouse.stop()
    while not event.getKeys(['esc', 'escape']):
        clicks, pos, scroll = toon_mouse.read()
        if pos is not None:
            print((pos[-1], pos[-1].time))
            pos *= [1, -1]
            for i in pos:
                toon_cir.pos += i
        psy_cir.pos = psy_mouse.getPos()
        psy_cir.draw()
        toon_cir.draw()
        win.flip()

win.close()
core.quit()
