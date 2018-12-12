from collections import namedtuple
from toon.anim.easing import linear
from toon.anim.interpolators import lerp, select


class Track(object):
    def __init__(self, data, interpolator=lerp, easing=linear):
        # data is list of tuples
        self.data = data
        self.interpolator = interpolator
        self.easing = easing
        # if data is non-numeric, force user to use select
        if not isinstance(data[0][1], (float, int)):
            self.interpolator = select
            self.easing = linear

    def at(self, time):
        # find the two keyframes to interpolate between
        # rel_time is the time relative to the start
        if time < self.data[0][0]:
            # TODO: extrapolation (currently equivalent to constant)
            return self.data[0][1]
        try:
            index, goal = next((i, x) for i, x in enumerate(self.data) if x[0] > time)
        except StopIteration:
            # TODO: Extrapolation (currently equivalent to constant)
            return self.data[-1][1]
        # prev keyframe to check against
        reference = self.data[index - 1]
        # calculate time stuff
        goal_time = goal[0] - reference[0]
        new_time = time - reference[0]
        time_warp = self.easing(1 - ((goal_time - new_time)/goal_time))
        return self.interpolator(reference[1], goal[1], time_warp)

    def duration(self):
        # last time in keyframes
        return self.data[-1][0]
