import numpy as np
from psychopy import visual, core, event
from psychopy.visual.circle import Circle
from toon.input.mpdevice import MpDevice
from toon.input.mouse import Mouse
from toon.anim.easing import linear
from toon.anim import Timeline, Track, Player


class AnimCircle(Player, Circle):
    def __init__(self, *args, **kwargs):
        Player.__init__(self)
        Circle.__init__(self, *args, **kwargs)


win = visual.Window(fullscr=True, units='pix')

timeline = Timeline()
timeline.start()
psy_mouse = event.Mouse()
toon_mouse = MpDevice(Mouse)

target_cir = AnimCircle(win, size=100, fillColor='white', lineColor=None)
toon_cir = visual.Circle(win, size=20, fillColor='blue', opacity=0.5, lineColor=None)
toon_cir.pos = (-win.size[0]/2, win.size[1]/2)

times = np.arange(0, 10, 1/60)
keyframes = np.vstack((times, np.sin(times) * 400)).T
keyframes2 = np.vstack((times, np.cos(times) * 400)).T
x_track = Track(keyframes, easing=linear)
y_track = Track(keyframes2, easing=linear)


def change_x(val, obj):
    obj.pos = [val, obj.pos[1]]


def change_y(val, obj):
    obj.pos = [obj.pos[0], val]


target_cir.add(x_track, change_x)
target_cir.add(y_track, change_y)
timeline.next_frame()
target_cir.start(timeline.frame_time)
with toon_mouse:  # alternatively, use toon_mouse.start(), toon_mouse.stop()
    while target_cir.is_playing() and not event.getKeys(['esc', 'escape']):
        win.callOnFlip(timeline.next_frame)
        target_cir.advance(timeline.frame_time)
        clicks, pos, scroll = toon_mouse.read()
        if pos is not None:
            pos *= [1, -1]
            for i in pos:
                toon_cir.pos += i
        if toon_cir.overlaps(target_cir):
            target_cir.fillColor = 'lightgray'
        else:
            target_cir.fillColor = 'white'
        target_cir.draw()
        toon_cir.draw()
        win.flip()

win.close()
core.quit()
