from timeit import default_timer

from psychopy import core, event, visual
from psychopy.visual.rect import Rect

from toon.anim.easing import (elastic_in_out, smootherstep, smoothstep,
                              exponential_out, linear)
from toon.anim.interpolators import select, lerp
from toon.anim import Timeline
from toon.anim import Track
from toon.anim import Player

keyfr = [(0.0, -0.5),
         (2.5, 0.5),
         (5.0, 0)]
lin_track = Track(keyfr, easing=linear)
elastic_track = Track(keyfr, easing=elastic_in_out)
smooth_track = Track([(0.0, 0.1),
                      (2.5, 0.2),
                      (5.0, 0.1)],
                     easing=smootherstep)

rotation_track = Track([(0.0, 0),
                        (2.3, 120),
                        (3.4, -44)],
                       easing=smoothstep)


col1_track = Track([(0.0, 0.6),
                    (0.4, 0.2),
                    (1.4, 1),
                    (2.6, -0.2),
                    (4.0, 0)], easing=exponential_out)

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
expand_cir = visual.Circle(win, radius=0.1,
                           pos=(0, -0.3), fillColor='blue',
                           edges=8)

line = visual.Line(win, start=(0, 1), end=(0, -1))


class SpecialRect(Player, Rect):
    # I think this is a special situation related to psychopy;
    # normally, ought to be able to just do class X(Player, Foo): pass
    def __init__(self, *args, **kwargs):
        Player.__init__(self)
        Rect.__init__(self, *args, **kwargs)


rect = SpecialRect(win, width=0.2, height=0.1,
                   fillColor='orange', pos=(0.1, 0.1), opacity=1)

timeline = Timeline()

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

player.add(smooth_track, 'radius', expand_cir)
player.add(col1_track, set_col1, obj=elas_cir)
player.add(col2_track, 'fillColor', lin_cir)

# visual as Player
rect.add(smooth_track, 'width')
rect.add(rotation_track, set_ori)
rect.scale = 4

win.callOnFlip(player.start, 0)
win.callOnFlip(rect.start, 0)
win.callOnFlip(timeline.start)

lin_cir.draw()
elas_cir.draw()
expand_cir.draw()
rect.draw()
line.draw()
win.flip()
t0 = default_timer()

while not event.getKeys():
    win.callOnFlip(timeline.next_frame)
    #print((timeline.frame_time, lin_cir.pos))
    player.advance(timeline.frame_time + 1/60)
    rect.advance(timeline.frame_time + 1/60)
    rect.draw()
    lin_cir.draw()
    elas_cir.draw()
    expand_cir.draw()
    line.draw()
    if default_timer() - t0 > 9.0:
        player.start(timeline.frame_time)
        # delay animation
        rect.start(timeline.frame_time + 1.5)
        t0 = default_timer()
    elif default_timer() - t0 > 7.3:
        player.stop()

    win.flip()

win.close()
