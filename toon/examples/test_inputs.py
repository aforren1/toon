from time import sleep
import sys
from distutils import util
import argparse
from platform import system
from toon.input import Keyboard, Hand, BlamBirds, DebugKeyboard, DummyTime
import numpy as np
if system() is 'Windows':
    from toon.input import ForceTransducers

# Call via
# python -m toon.examples.test_inputs --dev keyboard --mp True
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
                        type=lambda x: bool(util.strtobool(x)))
    results = parser.parse_args()

    mp = results.mp
    device = results.dev
    if not_travis:
        timer = core.monotonicClock
    else:
        timer = DummyTime()

    if device == 'keyboard':
        dev = Keyboard(multiprocess=mp, keys=['a', 's', 'd', 'f'], clock_source=timer)
    elif device == 'hand':
        dev = Hand(multiprocess=mp, clock_source=timer)
    elif device == 'birds':
        # settings for my laptop
        dev = BlamBirds(multiprocess=mp, ports=['COM11', 'COM12', 'COM13', 'COM10'],
                        master='COM11', sample_ports=['COM11', 'COM13'],
                        clock_source=timer)
    elif device == 'dbkeyboard':
        dev = DebugKeyboard(multiprocess=mp, keys=['a', 's', 'd', 'f'], clock_source=timer)
    elif device == 'forcetransducers':
        dev = ForceTransducers(multiprocess=mp, clock_source=timer)
    else:
        print('Pass the device as the first arg, and True/False as the second (for multiprocessing)')
        print("Available devices are: 'keyboard', 'hand', 'birds', 'dbkeyboard', 'forcetransducers'")
        sys.exit()

    with dev as d:
        t0 = timer.getTime()
        t1 = t0 + 10
        while timer.getTime() < t1:
            timestamp, data = d.read()
            if data is not None:
                print(timestamp - t0)
                print(data)
            sleep(0.016)

    sys.exit()