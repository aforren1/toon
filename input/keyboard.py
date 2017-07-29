from input.input_base import InputBase
import keyboard
from ctypes import windll

user32 = windll.user32

user32.ShowCursor(False)

user32.ShowCursor(True)

# http://www.psychopy.org/api/iohub/device/keyboard.html
