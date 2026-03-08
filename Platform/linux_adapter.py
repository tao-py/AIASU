from Xlib import display

class LinuxCursor:

    def get_position(self):

        data = display.Display().screen().root.query_pointer()._data

        return (data["root_x"], data["root_y"])