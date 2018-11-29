from collections import namedtuple
from toon.anim.easing import lerp, linear, select


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
        self.state = 'stopped'

    def start(self, time):
        self.time = time
        self.state = 'playing'

    def update(self, time):
        if self.state == 'stopped':
            return

        # find the two keyframes to interpolate between
        # rel_time is the time relative to the start
        rel_time = time - self.time
        try:
            index, goal = next((i, x) for i, x in enumerate(self.data) if x[0] > rel_time)
        except StopIteration:
            self.state = 'stopped'
            return self.data[-1][1]
        # prev keyframe to check against
        reference = self.data[index - 1]
        # calculate time stuff
        goal_time = goal[0] - reference[0]
        new_time = rel_time - reference[0]
        time_warp = self.easing(1 - ((goal_time - new_time)/goal_time))
        return self.interpolator(reference[1], goal[1], time_warp)


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    from toon.anim.easing import elastic_in_out
    trk = Track([(0.0, 1.0), (1.0, 1.5), (3, 0.0), (6.0, 5)],
                easing=elastic_in_out)
    trk.start(0)
    vals = []
    x = np.arange(0, 7, 1/60)
    for i in x:
        vals.append(trk.update(i))

    plt.plot(x, vals)
    plt.show()
