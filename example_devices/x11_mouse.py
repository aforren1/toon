
import ctypes as c
from ctypes.util import find_library
from toon.input.device import BaseDevice

x11path = find_library('X11')
if not x11path:
    raise ImportError('Could not find the X11 library.')

x11 = c.cdll.LoadLibrary(x11path)
x11.XInitThreads()
# some tips:
# https://stackoverflow.com/questions/29638210/how-can-i-use-python-xlib-to-generate-a-single-keypress
# https://github.com/kripken/intensityengine/blob/master/src/python/intensity/components/thirdparty/Skype4Py/api/posix_x11.py
c_ulong_p = c.POINTER(c.c_ulong)
DisplayP = c.c_void_p
Atom = c.c_ulong
AtomP = c_ulong_p
XID = c.c_ulong
Window = XID
Bool = c.c_int
Status = c.c_int
Time = c.c_ulong
c_int_p = c.POINTER(c.c_int)

align = (c.sizeof(c.c_long) == 8 and c.sizeof(c.c_int) == 4)

_base_fields = [
    ('type', c.c_int),
    ('serial', c.c_ulong),
    ('send_event', Bool),
    ('display', DisplayP),
    ('window', Window),
    ('root', Window),
    ('subwindow', Window),
    ('time', Time),
    ('x', c.c_int),
    ('y', c.c_int),
    ('x_root', c.c_int),
    ('y_root', c.c_int),
    ('state', c.c_uint),
    # ('keycode', c.c_uint),
    ('same_screen', Bool),
]

key_fields = _base_fields.copy()
key_fields.insert(-1, ('keycode', c.c_uint))
button_fields = _base_fields.copy()
button_fields.insert(-1, ('button', c.c_uint))
motion_fields = _base_fields.copy()
motion_fields.insert(-1, ('is_hint', c.c_char))


class XKeyEvent(c.Structure):
    _fields_ = key_fields


class XButtonEvent(c.Structure):
    _fields_ = button_fields


class XMotionEvent(c.Structure):
    _fields_ = motion_fields


class XEvent(c.Union):
    _fields_ = [
        ('type', c.c_int),
        ('xkey', XKeyEvent),
        ('xbutton', XButtonEvent),
        ('xmotion', XMotionEvent),
        ('pad', c.c_long*24),
    ]


XEventP = c.POINTER(XEvent)
x11.XOpenDisplay.restype = DisplayP


class X11Mouse(BaseDevice):
    sampling_frequency = 1000  # optimistic
    shape = (1,)
    ctype = None

    def enter(self):
        disp = x11.XOpenDisplay(None)  # root window
