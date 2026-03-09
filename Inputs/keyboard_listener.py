from pynput import keyboard
import threading

class KeyboardListener:

    def __init__(self, callback):
        self.buffer = ""
        self.callback = callback
        self.listener = None
        self.running = False

    def on_press(self, key):
        try:
            if key.char:
                self.buffer += key.char

                if key.char == " ":
                    text = self.buffer.strip()
                    if text:
                        self.callback(text)
                    self.buffer = ""
            elif key == keyboard.Key.enter:
                text = self.buffer.strip()
                if text:
                    self.callback(text)
                self.buffer = ""
            elif key == keyboard.Key.backspace:
                if self.buffer:
                    self.buffer = self.buffer[:-1]
        except AttributeError:
            # 处理特殊键
            pass
        except Exception as e:
            print(f"Keyboard listener error: {e}")

    def start(self):
        if self.running:
            return
        self.running = True
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        print("Keyboard listener started")

    def stop(self):
        if self.listener and self.running:
            self.listener.stop()
            self.running = False
            print("Keyboard listener stopped")