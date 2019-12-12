from collections import namedtuple
from toon.anim.easing import linear
from toon.anim.interpolators import lerp, select


class Track(object):
    """Storage for (keyframe, value) pairs.

    Also handles interpolation and easing between keyframes.
    """

    def __init__(self, data, interpolator=lerp, easing=linear):
        """Creates a Track.

        Parameters
        ----------
        data: list of (keyframe, value) pairs. 
            These are expected to be sorted by keyframe in ascending order.
            Keyframe should not be duplicated.
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
        self.prev_index = 0
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

        # handle boundaries first
        data = self.data

        if time <= data[0][0]:
            self.prev_index = 0
            return data[0][1]

        if time >= data[-1][0]:
            self.prev_index = len(data) - 1
            return data[-1][1]

        # extract previous keyframe
        prev_index = self.prev_index
        prev_kf = data[prev_index]
        if time == prev_kf[0]:
            return prev_kf[1]

        sign = time - prev_kf[0]
        len_data = len(data)

        # if time is greater than previous keyframe time, search toward end
        if sign > 0:
            offset = -1
            for index in range(self.prev_index + 1, len_data):
                #print('a%i' % index)
                # find the next keyframe that the current time is less than
                proposed_kf = data[index]
                if time < proposed_kf[0]:
                    kf = proposed_kf
                    break
        # if time is less than previous keyframe time, search toward beginning
        elif sign < 0:
            offset = 1
            for index in range(self.prev_index - 1, -1, -1):
                #print('b%i' % index)
                # find the next keyframe that the current time is greater than
                proposed_kf = data[index]
                if time > proposed_kf[0]:
                    kf = proposed_kf
                    break
        else:
            raise ValueError('Unexpected value.')

        self.prev_index = index
        # find the other keyframe to interpolate between
        reference = data[index + offset]
        # print('kf_ref: %s, time: %s, kf_targ: %s' % (reference, time, kf))
        goal_time = kf[0] - reference[0]
        new_time = time - reference[0]
        time_warp = self.easing(1 - ((goal_time - new_time)/goal_time))
        return self.interpolator(reference[1], kf[1], time_warp)

    def duration(self):
        """The maximum duration of the track."""
        # last time in keyframes
        return self.data[-1][0]
