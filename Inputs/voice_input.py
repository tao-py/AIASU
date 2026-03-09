import requests
import threading
import time

class VoiceInput:

    def __init__(self, callback):
        self.callback = callback
        self.api = "http://localhost:8000/stt"
        self.running = False
        self.thread = None
        self.last_text = ""

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()
        print("Voice input started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("Voice input stopped")

    def listen(self):
        """监听语音输入"""
        while self.running:
            try:
                r = requests.get(self.api, timeout=2)
                if r.status_code == 200:
                    text = r.json().get("text", "").strip()
                    if text and text != self.last_text:
                        self.last_text = text
                        self.callback(text)
            except requests.exceptions.RequestException:
                # API未启动或其他网络问题，静默处理
                time.sleep(1)
            except Exception as e:
                print(f"Voice input error: {e}")
                time.sleep(1)