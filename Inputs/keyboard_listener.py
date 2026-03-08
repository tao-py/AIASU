from pynput import keyboard

class KeyboardListener:

    def __init__(self, callback):

        self.buffer = ""
        self.callback = callback

    def on_press(self, key):

        try:
            if key.char:
                self.buffer += key.char

                if key.char == " ":
                    self.callback(self.buffer)
                    self.buffer = ""

        except:
            pass

    def start(self):

        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()