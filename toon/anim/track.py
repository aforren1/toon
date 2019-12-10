from collections import namedtuple
from toon.anim.easing import linear
from toon.anim.interpolators import lerp, select
from timeit import default_timer


class Track(object):
    """Storage for (keyframe, value) pairs.

    Also handles interpolation and easing between keyframes.
    """

    def __init__(self, data, interpolator=lerp, easing=linear):
        """Creates a Track.

        Parameters
        ----------
        data: list of (keyframe, value) pairs
        interpolator: function
            `lerp` for linear interpolation, `select` for stepwise behavior.
        easing: function
            Rate of change of the value over time. See toon.anim.easing, or
            specificy a custom function that takes a single parameter, and
            returns a value on the interval [0, 1].
        """
        # data is list of tuples
        self.data = data
        self.interpolator = interpolator
        self.easing = easing
        self.prev = 0
        # if data is non-numeric, force user to use select
        if not isinstance(data[0][1], (float, int)):
            self.interpolator = select
            self.easing = linear

    def at(self, time):
        """Get the interpolated value of a track at a given time.

        Parameters
        ----------
        time: float
            Time of interest.

        Returns
        -------
        The interpolated value at the given point in time.
        """
        data = self.data
        # handle boundaries first
        if time <= data[0][0]:
            self.prev = 0
            return data[0][1]

        if time >= data[-1][0]:
            self.prev = len(data)
            return data[-1][1]
        # iterate from previous index
        len_data = len(data)
        kf = None
        for idx in range(self.prev, len_data):
            if data[idx][0] > time:
                kf = data[idx]
                break
        # if we don't find it searching forward, start at beginning
        if kf is None:
            for idx in range(len_data):
                if data[idx][0] > time:
                    kf = data[idx]
                    break
        # TODO: kf *should* exist at this point, but do we need more error checking?
        self.prev = idx
        reference = data[self.prev-1]
        goal_time = kf[0] - reference[0]
        new_time = time - reference[0]
        time_warp = self.easing(1 - ((goal_time - new_time)/goal_time))
        return self.interpolator(reference[1], kf[1], time_warp)

    def duration(self):
        """The maximum duration of the track."""
        # last time in keyframes
        return self.data[-1][0]
