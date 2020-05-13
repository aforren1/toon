from timeit import default_timer

from psychopy import core, event, visual
from psychopy.visual.rect import Rect

from toon.anim.easing import (ELASTIC_IN_OUT, SMOOTHERSTEP, SMOOTHSTEP,
                              EXPONENTIAL_OUT, LINEAR)
from toon.anim.interpolators import SELECT, LERP
from toon.anim import Track
from toon.anim import Player

keyfr = [(0.0, -0.5),
         (2.5, 0.5),
         (5.0, 0)]
lin_track = Track(keyfr, easing=LINEAR)
elastic_track = Track(keyfr, easing=ELASTIC_IN_OUT)
smooth_track = Track([(0.0, 0.1),
                      (2.5, 0.2),
                      (5.0, 0.1)],
                     easing=SMOOTHERSTEP)

rotation_track = Track([(0.0, 0),
                        (2.3, 120),
                        (3.4, -44)],
                       easing=SMOOTHSTEP)


col1_track = Track([(0.0, 0.6),
                    (0.4, 0.2),
                    (1.4, 1),
                    (2.6, -0.2),
                    (4.0, 0)], easing=EXPONENTIAL_OUT)

# easing doesn't matter here
col2_track = Track([(0, 'black'),
                    (1.25, 'blue'),
                    (2.5, 'green'),
                    (5, 'black')])

win = visual.Window(units='height', fullscr=True, waitBlanking=False)

lin_cir = visual.Circle(win, radius=0.1,
                        pos=(-0.3, 0.3), fillColor='red',
                        edges=8)
elas_cir = visual.Circle(win, radius=0.1,
                         pos=(-0.3, 0), fillColor=[1, 1, 1],
                         edges=8)
expand_rect = visual.Rect(win, width=0.1, height=0.15,
                           pos=(0, -0.3), fillColor='blue')

line = visual.Line(win, start=(0, 1), end=(0, -1))

player = Player()

def set_pos(val, obj, **kwargs):
    obj.pos = [val, obj.pos[1]]


def set_col1(val, obj, **kwargs):
    obj.fillColor = [obj.fillColor[0], val, obj.fillColor[2]]


def set_ori(val, obj, **kwargs):
    obj.ori = val


# Player dictating several visual changes
# TODO: callbacks once time reached?
player.add(lin_track, set_pos, obj=lin_cir)
player.add(elastic_track, set_pos, obj=elas_cir)

player.add(smooth_track, 'width', expand_rect)
player.add(col1_track, set_col1, obj=elas_cir)
player.add(col2_track, 'fillColor', lin_cir)

win.callOnFlip(player.start, 0)

lin_cir.draw()
elas_cir.draw()
expand_rect.draw()
line.draw()
win.flip()
t0 = default_timer()

while not event.getKeys():
    #print((timeline.frame_time, lin_cir.pos))
    player.advance(default_timer() - t0 + 1/60)
    lin_cir.draw()
    elas_cir.draw()
    expand_rect.draw()
    line.draw()
    if default_timer() - t0 > 9.0:
        # delay animation
        t0 = default_timer()
        player.start(t0)
    elif default_timer() - t0 > 7.3:
        player.stop()

    win.flip()

win.close()
