from input.input_base import InputBase
from psychopy import event
# use from keyboard import mouse?
# only thing is hiding the mouse/unhiding on failure

class Mouse(InputBase):
    def __init__(self, clock_source=None, visible=True, win=None):
        super(Mouse, self).__init__(clock_source)
        self.mouse = event.Mouse(visible=visible, win=win)

    def start(self):
        return
    def stop(self):
        return
    def close(self):
        return
    def write(self, data):
        return
    def _world_to_raw(self):
        return [self.clock,
                self.mouse.getRel(),
                self.mouse.getPos(),
                self.mouse.getPressed(getTime=True),
                self.mouse.getWheelRel()]

    
    # inputs available from mice:
    # relative position (getRel())
    # absolute position (getPos())
    # key presses (getPressed(getTime=True)) (call w/clickReset() to reset timers)
    ## note that the time returned by keypresses is not frame-dependent
    # wheel pos (getWheelRel())

    # event.clearEvents() to clear events
