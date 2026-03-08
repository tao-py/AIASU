import pyperclip
import time

class ClipboardMonitor:

    def start(self):

        last = ""

        while True:

            text = pyperclip.paste()

            if text != last:
                last = text

            time.sleep(1)