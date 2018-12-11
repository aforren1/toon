from inspect import ismethod
from collections import namedtuple
from copy import copy

TrackAttr = namedtuple('TrackAttr', 'track attr obj kwargs')


class Player(object):
    def __init__(self, *args, **kwargs):
        self.tracks = []
        self.state = 'stopped'  # 'playing', 'paused'
        self.ref_time = None
        self.stop_pause_time = None
        self.duration = 0

    def add(self, track, attr, obj=None, **kwargs):
        self.tracks.append(TrackAttr(copy(track), attr, obj, kwargs))
        new_dur = track.duration()
        self.duration = new_dur if new_dur > self.duration else self.duration

    def start(self, time):
        if self.state == 'paused':
            self.ref_time = time - self.ref_time
        else:
            self.ref_time = time
        self.state = 'playing'

    def pause(self, time):
        if self.state != 'playing':
            return
        self.state = 'paused'
        self.stop_pause_time = time

    def stop(self):
        self.state = 'stopped'

    def resume(self, time):
        if self.state == 'playing':
            return
        self.start(time)

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

    def advance(self, time):
        if self.state != 'playing':
            return
        if time < self.ref_time:
            return
        for trk in self.tracks:
            # if tracks are playing, will return a val
            val = trk.track.at(time - self.ref_time)
            if trk.obj:  # object or list provided, so we'll manipulate them
                try:  # see if single object
                    self._do_update(trk.attr, val,
                                    trk.obj, **trk.kwargs)
                except (TypeError, AttributeError):  # list of objects?
                    for obj in trk.obj:
                        self._do_update(trk.attr, val,
                                        obj, **trk.kwargs)
            else:  # operate on self
                self._do_update(trk.attr, val, self, **trk.kwargs)
            # if we've gone beyond, stop playing
            if time - self.ref_time >= self.duration:
                self.state = 'stopped'

    def is_playing(self):
        return self.state == 'playing'

    def is_paused(self):
        return self.state == 'paused'

    def is_stopped(self):
        return self.state == 'stopped'

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._state = val
