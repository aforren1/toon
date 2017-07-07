from __future__ import division
from __future__ import print_function

# author Jeremy Gray

from psychopy import visual, event, monitors
from psychopy.tools.coordinatetools import pol2cart

mon = monitors.Monitor('tmp')
mon.setSizePix((1920, 1200))
mon.setWidth(52)
win = visual.Window(size=(1920, 1200), fullscr=True, screen=1, monitor=mon, units='cm')

vm = event.Mouse(visible=False)
#vm = visual.CustomMouse(win)
#vm.setLimit(leftLimit=-1, rightLimit=1, bottomLimit=-1, topLimit=1)
pointer = visual.Circle(win, radius=1.27/2, fillColor='darkmagenta',
                        pos=vm.getPos())

# target
target = visual.Circle(win, radius=2.54/2, fillColor='black',
                       pos=pol2cart(90, 10.16))
center = visual.Circle(win, radius = 2, fillColor='green', pos=(0,0))

while not event.getKeys():
    pointer.pos = vm.getPos()
    if target.contains(vm):
        target.fillColor='white'
    else:
        target.fillColor='black'
    
    #vm.draw()
    center.draw()
    target.draw()
    pointer.draw()
    win.flip()
    print(vm.getPos())

win.close()