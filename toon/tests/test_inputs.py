from time import sleep
import sys
from platform import system
from toon.input import Keyboard, Hand, BlamBirds, DebugKeyboard
from psychopy import core
import numpy as np
if system() is 'Windows':
    from toon.input import ForceTransducers

np.set_printoptions(precision=4, suppress=True)

if __name__=='__main__':

    device = str(sys.argv[1])
    mp = bool(sys.argv[2])

    timer = core.monotonicClock

    if device == 'keyboard':
        dev = Keyboard(multiprocess=mp, keys=['a', 's', 'd', 'f'], clock_source=timer)
    elif device == 'hand':
        dev = Hand(multiprocess=mp, clock_source=timer)
    elif device == 'birds':
        dev = BlamBirds(multiprocess=mp, ports=['COM11', 'COM12', 'COM13', 'COM14'],
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
                #print(data)
            sleep(0.016)

    sys.exit()