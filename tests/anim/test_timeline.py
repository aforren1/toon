from timeit import default_timer
from toon.anim.timeline import Timeline


def test_timeline():
    timeline = Timeline()
    timeline.start()
    timeline.next_frame()
    assert(abs(timeline.prev_frame_time - default_timer()) < 0.0001)
    assert(timeline.frame_time > 0)
    assert(timeline.delta_time > 0)
    timeline.stop()
    assert(not timeline.running)
    timeline.start()
    assert(timeline.running)
