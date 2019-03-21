from platform import system

sys = system()
if sys == 'Windows':
    from toon.input.clocks.win_clock import MonoClock
elif sys == 'Darwin':
    from toon.input.clocks.mac_clock import MonoClock
else:  # anything else uses timeit.default_timer
    from toon.input.clocks.default_clock import MonoClock

mono_clock = MonoClock()
