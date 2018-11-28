from collections import namedtuple
from copy import copy

TrackAttr = namedtuple('TrackAttr', 'track attr obj kwargs')


class Player(object):
    def __init__(self, *args, **kwargs):
        self.tracks = {}
        self.player_state = 'stopped'

    def add(self, name, track, attr, obj=None, **kwargs):
        if name in self.tracks:
            raise ValueError('Track name already exists.')
        self.tracks.update({name: TrackAttr(copy(track), attr, obj, kwargs)})

    def remove(self, name):
        self.tracks.pop(name, None)
        return

    def start(self, time, names=None):
        self.player_state = 'started'
        if not names:
            for i in self.tracks:
                self.tracks[i].track.start(time)
            return
        for i in names:
            self.tracks[i].track.start(time)

    def _do_update(self, attr, val, obj, **kwargs):
        # if we get a function, call function with updated val
        if callable(attr):
            attr(val, obj, **kwargs)
            return
        # otherwise (user gave string), directly set the attribute
        setattr(obj, attr, val)

    def update(self, time):
        if self.player_state == 'started':
            for i in self.tracks:
                # if tracks are playing, will return a val
                val = self.tracks[i].track.update(time)
                if val is not None:
                    if self.tracks[i].obj:  # object or list provided, so we'll manipulate them
                        try:  # see if single object
                            self._do_update(self.tracks[i].attr, val,
                                            self.tracks[i].obj, **self.tracks[i].kwargs)
                        except TypeError:  # list of objects?
                            for i in self.tracks[i].obj:
                                self._do_update(self.tracks[i].attr, val,
                                                self.tracks[i].obj, **self.tracks[i].kwargs)
                    else:  # operate on self
                        self._do_update(self.tracks[i].attr, val, self, **self.tracks[i].kwargs)

    def stop(self, names=None):
        self.player_state = 'stopped'
        if not names:
            for i in self.tracks:
                self.tracks[i].track.state = 'stopped'
            return
        for i in names:
            self.tracks[i].track.state = 'stopped'

    def state(self, name):
        return self.tracks[name].track.state


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    from toon.anim.track import Track
    from toon.anim.easing import elastic_in_out

    trk = Track([(0.0, 1.0), (1.0, 1.5), (3, 0.0), (6.0, 5)],
                easing=elastic_in_out)

    class Circ:
        def __init__(self):
            self.pos = [0, 0]

    circ = Circ()
    playa = Player()

    def cb(val, obj):
        obj.pos[0] = val

    playa.add('pos', trk, cb, obj=circ)

    playa.start(0)  # start all

    x = np.arange(0, 7, 1/60)
    vals = []
    for i in x:
        playa.update(i)
        vals.append(circ.pos[0])

    plt.plot(x, vals)
    plt.show()
