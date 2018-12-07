from inspect import ismethod
from collections import namedtuple
from copy import copy

TrackAttr = namedtuple('TrackAttr', 'track attr obj kwargs')


class Player(object):
    def __init__(self, *args, **kwargs):
        self.tracks = {}

    def add(self, name, track, attr, obj=None, **kwargs):
        if name in self.tracks:
            raise ValueError('Track name already exists.')
        self.tracks.update({name: TrackAttr(copy(track), attr, obj, kwargs)})

    def remove(self, names):
        if isinstance(names, list):
            for i in names:
                self.tracks.pop(i, None)
        else:
            self.tracks.pop(names, None)
        return

    def start(self, time, names=None):
        if not names:
            for i in self.tracks:
                self.tracks[i].track.start(time)
        elif isinstance(names, list):
            for i in names:
                self.tracks[i].track.start(time)
        else:
            self.tracks[names].track.start(time)

    def _do_update(self, attr, val, obj, **kwargs):
        # if we get a function, call function with updated val
        if callable(attr):
            # if it's a method (e.g. a setter), we call that method with the val as an arg
            if ismethod(attr):
                if kwargs:
                    attr(val, **kwargs)
                else:
                    attr(val)
                return
            if kwargs:
                attr(val, obj, **kwargs)
            else:
                attr(val, obj)
            return
        # otherwise (user gave string), directly set the attribute
        setattr(obj, attr, val)

    def update(self, time):
        for i in self.tracks:
            # if tracks are playing, will return a val
            val = self.tracks[i].track.update(time)
            if val is not None:
                if self.tracks[i].obj:  # object or list provided, so we'll manipulate them
                    try:  # see if single object
                        self._do_update(self.tracks[i].attr, val,
                                        self.tracks[i].obj, **self.tracks[i].kwargs)
                    except (TypeError, AttributeError):  # list of objects?
                        for obj in self.tracks[i].obj:
                            self._do_update(self.tracks[i].attr, val,
                                            obj, **self.tracks[i].kwargs)
                else:  # operate on self
                    self._do_update(self.tracks[i].attr, val, self, **self.tracks[i].kwargs)

    def stop(self, names=None):
        if not names:
            for i in self.tracks:
                self.tracks[i].track.state = 'stopped'
        elif isinstance(names, list):
            for i in names:
                self.tracks[i].track.state = 'stopped'
        else:
            # single key
            self.tracks[names].track.state = 'stopped'

    def is_playing(self, name):
        return self.tracks[name].track.state == 'playing'

    def any_playing(self):
        return any([self.tracks[x].track.state == 'playing' for x in self.tracks])
