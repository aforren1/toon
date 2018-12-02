import pytest
from collections import namedtuple
from toon.anim.player import Player
from toon.anim.track import Track
from toon.anim.easing import elastic_in

pos = namedtuple('pos', 'x y')


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
    player.add('x1', trk, 'x', circ)
    # callback
    player.add('x2', trk, change_val, circ2)

    player.start(0)
    assert(all([player.is_playing(x) for x in player.tracks]))
    player.update(0.5)
    assert(circ.x == circ2.x)
    player.stop(['x1'])
    player.update(0.9)
    assert(player.is_playing('x2'))
    assert(circ.x < circ2.x)
    player.update(1.0)
    # test if stops after track exhausted
    assert(not player.is_playing('x2'))
    # modifying a group of objects (with matching API)
    circs = [Circ() for i in range(5)]

    player.add('x3', trk, 'y', circs)
    player.start(0, ['x3'])
    player.update(0.5)
    assert(all([i.y == 0.5 for i in circs]))
    player.remove('x3')
    with pytest.raises(KeyError):
        player.tracks['x3']

    player.stop()
    assert(player.player_state == 'stopped')
    assert(all([not player.is_playing(x) for x in player.tracks]))

    def call(val, obj, foo):
        obj.x = val * foo

    player.add('x4', trk, call, circ, foo=2)
    player.start(0, ['x4'])
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
    circ.add('x', trk, 'x')
    # callback
    circ.add('y', trk, change_y)
    # drive another object
    circ.add('x2', trk, 'x', circ2)

    circ.start(0)
    circ.update(0.5)
    assert(circ.x == circ.y == circ2.x)
    with pytest.raises(ValueError):
        circ.add('x', trk, change_y)
