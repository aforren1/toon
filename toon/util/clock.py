from platform import system

sys = system()
if sys == 'Windows':
    from toon.util.clocks.win_clock import MonoClock
elif sys == 'Darwin':
    from toon.util.clocks.mac_clock import MonoClock
else:  # anything else uses timeit.default_timer
    from toon.util.clocks.default_clock import MonoClock

mono_clock = MonoClock()
