#cython: boundscheck=False
#cython: nonecheck=False
#cython: wraparound=False
#cython: infertypes=True
#cython: initializedcheck=False
#cython: cdivision=True
from copy import copy
from inspect import ismethod
ctypedef enum states: STOPPED, PLAYING

cdef class Player:
    
    cdef public int repeats
    cdef int _repeats
    cdef states state
    cdef double ref_time
    cdef double duration
    cdef public double timescale
    cdef list tracks
    cdef list prev_vals

    def __init__(self, int repeats=1):
        self.tracks = []
        self.state = STOPPED
        self.ref_time = 0
        self.duration = 0
        self.timescale = 1
        self.prev_vals = []
        self.repeats = repeats
        self._repeats = repeats # track
    
    def add(self, track, attr, obj, **kwargs):
        self.tracks.append({'track': track, 'attr': attr, 
                            'obj': obj, 'kwargs': kwargs})
        self.prev_vals.append(None)
        new_dur = track.duration()
        if new_dur > self.duration:
            self.duration = new_dur
        
    cpdef start(self, const double time):
        self.ref_time = time
        self._repeats = self.repeats
        self.state = PLAYING
        self.advance(time)
    
    cpdef stop(self):
        self.state = STOPPED
    
    cpdef reset(self):
        self.advance(self.ref_time)
        self.state = STOPPED
    
    cpdef resume(self, const double time):
        if self.state == PLAYING:
            return
        self.start(time)

    cpdef advance(self, const double time):
        """Update all Tracks with a new time.
        Parameters
        ----------
        time: float
            Current time. Track time is `time - reference time`.
        """
        if self.state != PLAYING:
            return
        if time < self.ref_time:
            return
        cdef double time2 = time
        # if we've gone beyond, stop playing after one more iteration
        if time - self.ref_time >= self.duration:
            self._repeats -= 1
            if self._repeats < 1:
                self.state = STOPPED
                time2 = self.ref_time + self.duration
            else:
                self.ref_time = self.ref_time + self.duration
        for counter, trk in enumerate(self.tracks):
            # if tracks are playing, will return a val
            val = trk['track'].at((time2 - self.ref_time) * self.timescale)
            prev_val = self.prev_vals[counter]
            self.prev_vals[counter] = val
            if val == prev_val:
                continue
            # unpack
            attr = trk['attr']
            obj = trk['obj']
            kwargs = trk['kwargs']
            try:  # see if single object
                self._do_update(attr, val, obj, **kwargs)
            except (TypeError, AttributeError):  # list of objects?
                for o in obj:
                    self._do_update(attr, val, o, **kwargs)


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

    @property
    def is_playing(self):
        return self.state == PLAYING

    @property
    def is_stopped(self):
        return self.state == STOPPED
