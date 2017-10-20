from time import sleep
import sys
from distutils import util
import argparse
from platform import system
from toon.input import Keyboard, Hand, BlamBirds, MultiprocessInput
import numpy as np
if system() is 'Windows':
    from toon.input import ForceTransducers
import matplotlib.pyplot as plot

# Call via
# python -m toon.examples.try_inputs --dev keyboard --mp True --time 10
import os
not_travis = 'TRAVIS' not in os.environ
if not_travis:
    from psychopy import core

np.set_printoptions(precision=4, suppress=True)

if __name__=='__main__':

    parser = argparse.ArgumentParser(description="My parser")
    parser.add_argument('--dev',
                        dest='dev')
    parser.add_argument('--mp',
                        dest='mp',
                        type=lambda x: bool(util.strtobool(x)),
                        default=False)
    parser.add_argument('--time',
                        dest='dur', default=5)
    parser.add_argument('--print', dest='print', default=True)
    parser.add_argument('--plot', dest='plot', default=False)
    results = parser.parse_args()

    mp = results.mp
    device = results.dev
    duration = float(results.dur)
    prnt = bool(results.print)
    plt = bool(results.plot)

    if not_travis:
        time = core.monotonicClock.getTime
    else:
        from timeit import default_timer
        time = default_timer
    if device == 'keyboard':
        dev = Keyboard(keys=['a', 's', 'd', 'f'], clock_source=time)
    elif device == 'hand':
        dev = Hand(clock_source=time)
    elif device == 'birds':
        # settings for my laptop
        dev = BlamBirds(ports=['COM11', 'COM12', 'COM13', 'COM10'],
                        master='COM11',
                        sample_ports=['COM11', 'COM13'],
                        clock_source=time)
    elif device == 'forcetransducers':
        dev = ForceTransducers(clock_source=time)
    else:
        print('Pass the device as the first arg, and True/False as the second (for multiprocessing)')
        print("Available devices are: 'keyboard', 'hand', 'birds', 'forcetransducers'")
        sys.exit()
    if mp:
        device = MultiprocessInput(dev)
    else:
        device = dev
    lst = list()
    with device as d:
        t0 = time()
        t1 = t0 + duration
        while time() < t1:
            t2 = time()
            t3 = t2 + 0.016
            data = d.read()
            if data is not None:
                if prnt:
                    print([d['data'] for d in data])
                lst.extend([d['time'] for d in data])
            while time() < t3:
                pass
    if plt:
        d = np.diff(lst)
        plot.plot(d)
        plot.show()
        plot.hist(d)
        plot.show()

    sys.exit()