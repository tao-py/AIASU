import pyperclip
import time
import threading

class ClipboardMonitor:

    def __init__(self, callback=None):
        self.callback = callback
        self.running = False
        self.thread = None
        self.last_text = ""

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.monitor, daemon=True)
        self.thread.start()
        print("Clipboard monitor started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("Clipboard monitor stopped")

    def monitor(self):
        """监控剪贴板变化"""
        while self.running:
            try:
                text = pyperclip.paste()
                if text and text != self.last_text:
                    self.last_text = text
                    if self.callback:
                        self.callback(text)
            except Exception:
                pass
            time.sleep(0.5)