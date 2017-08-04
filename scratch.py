from __future__ import division
from __future__ import print_function

from psychopy import visual, event, monitors
from psychopy.tools.coordinatetools import pol2cart
#from input.mouse import Mouse

mon = monitors.Monitor('tmp')
mon.setSizePix((1536, 864))
mon.setWidth(29.37)
win = visual.Window(size=(1536, 864), fullscr=True, 
                    screen=0, monitor=mon, units='cm')

vm = event.Mouse(visible=False)
#vm = Mouse()

#def get_pos(values):
#    return values[2]

#vm._raw_to_exp = get_pos

pointer = visual.Circle(win, radius=1.27/2, fillColor='darkmagenta',
                        pos=vm.getPos())

# target
target = visual.Circle(win, radius=2.54/2, fillColor='black',
                       pos=pol2cart(90, 5.08))
center = visual.Circle(win, radius = 2, fillColor='green', pos=(0,0))

while not event.getKeys():
    pointer.pos = vm.getPos()
    if target.contains(pointer.pos):
        target.fillColor = 'white'
    else:
        target.fillColor = 'black'
    
    # vm.draw()
    center.draw()
    target.draw()
    pointer.draw()
    win.flip()
    print(vm.getPos())
    #print(vm.read())
win.close()
