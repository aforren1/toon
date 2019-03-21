from platform import system

# From Stack Overflow
# User linusg https://stackoverflow.com/users/5952681/linusg
# https://stackoverflow.com/a/38463185/2690232

sys = system()
if sys == 'Windows':
    from toon.input.clocks.win_clock import MonoClock
elif sys == 'Darwin':
    from toon.input.clocks.mac_clock import MonoClock
else:  # anything else uses timeit.default_timer
    from toon.input.clocks.default_clock import MonoClock

mono_clock = MonoClock()
