import requests
import threading

class VoiceInput:

    def __init__(self, callback):

        self.callback = callback
        self.api = "http://localhost:8000/stt"

    def start(self):

        threading.Thread(target=self.listen).start()

    def listen(self):

        while True:

            r = requests.get(self.api)

            if r.status_code == 200:

                text = r.json()["text"]

                if text:
                    self.callback(text)