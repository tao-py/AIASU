import ctypes
from ctypes import wintypes

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG),
                ("y", wintypes.LONG)]

class WindowsCursor:

    def get_position(self):

        pt = POINT()

        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))

        return (pt.x, pt.y)