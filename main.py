from Inputs.keyboard_listener import KeyboardListener
from Inputs.voice_input import VoiceInput
from Inputs.clipboard_monitor import ClipboardMonitor
from Context.app_detector import AppDetector
from Ai.agent_router import AgentRouter
from Ui.overlay_window import OverlayWindow

class AIInputAssistant:

    def __init__(self):

        self.app_detector = AppDetector()
        self.agent_router = AgentRouter()

        self.overlay = OverlayWindow()

        self.keyboard = KeyboardListener(self.on_text_input)
        self.voice = VoiceInput(self.on_voice_input)
        self.clipboard = ClipboardMonitor()

    def on_text_input(self, text):

        app = self.app_detector.detect()

        candidates = self.agent_router.generate(text, app)

        self.overlay.show_candidates(candidates)

    def on_voice_input(self, text):

        app = self.app_detector.detect()

        candidates = self.agent_router.generate(text, app)

        self.overlay.show_candidates(candidates)

    def run(self):

        self.keyboard.start()
        self.voice.start()
        self.clipboard.start()

        self.overlay.run()


if __name__ == "__main__":

    app = AIInputAssistant()
    app.run()