import pytest
from collections import namedtuple
from toon.anim.player import Player
from toon.anim.track import Track


class Circ(object):
    def __init__(self):
        self.x = 0
        self.y = 0


def test_player():
    trk = Track([(0, 0), (0.5, 0.5), (1, 1)])
    circ = Circ()
    circ2 = Circ()

    def change_val(val, obj):
        obj.x = val

    player = Player()
    # directly access an attribute
    player.add(trk, 'x', circ)
    # callback
    player.add(trk, change_val, circ2)

    player.start(0)
    assert(player.is_playing())
    player.update(0.5)
    assert(circ.x == circ2.x)
    player.update(0.9)
    assert(circ.x == circ2.x)
    player.update(1.0)
    # test if stops after track exhausted
    assert(not player.is_playing())
    # modifying a group of objects (with matching API)
    circs = [Circ() for i in range(5)]

    player.add(trk, 'y', circs)
    player.start(0)
    player.update(0.5)
    assert(all([i.y == 0.5 for i in circs]))

    player.stop()
    assert(not player.is_playing())

    def call(val, obj, foo):
        obj.x = val * foo

    player.add(trk, call, circ, foo=2)
    player.start(0)
    player.update(0.5)
    assert(circ.x == 1)


def test_player_mixin():
    class CircMix(Player, Circ):
        pass

    trk = Track([(0, 0), (0.5, 0.5), (1, 1)])

    def change_y(val, obj):
        obj.y = val
    circ = CircMix()
    circ2 = Circ()
    # change directly
    circ.add(trk, 'x')
    # callback
    circ.add(trk, change_y)
    # drive another object
    circ.add(trk, 'x', circ2)

    circ.start(0)
    circ.update(0.5)
    assert(circ.x == circ.y == circ2.x)
