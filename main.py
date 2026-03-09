import sys
from PySide6.QtWidgets import QApplication
from Inputs.keyboard_listener import KeyboardListener
from Inputs.voice_input import VoiceInput
from Inputs.clipboard_monitor import ClipboardMonitor
from Context.app_detector import AppDetector
from Ai.agent_router import AgentRouter
from Ui.overlay_window import OverlayWindow
from Platform.cursor_anchor import CursorAnchor

class AIInputAssistant:

    def __init__(self):
        self.cursor_anchor = CursorAnchor()
        self.app_detector = AppDetector()
        self.agent_router = AgentRouter()
        self.overlay = OverlayWindow()

        self.keyboard = KeyboardListener(self.on_text_input)
        self.voice = VoiceInput(self.on_voice_input)
        self.clipboard = ClipboardMonitor(self.on_clipboard_input)

        # 应用上下文缓存
        self.current_context = {}

    def on_text_input(self, text):
        """处理文本输入"""
        try:
            # 获取应用上下文
            app_info = self.app_detector.detect()
            self.current_context = app_info

            # 获取光标位置
            cursor_pos = self.cursor_anchor.get_position()

            # 生成候选
            candidates = self.agent_router.generate(text, app_info)

            # 显示候选窗口
            self.overlay.show_candidates(candidates)
            self.overlay.move_to_cursor(cursor_pos)
        except Exception as e:
            print(f"Error in on_text_input: {e}")

    def on_voice_input(self, text):
        """处理语音输入"""
        try:
            app_info = self.app_detector.detect()
            self.current_context = app_info
            cursor_pos = self.cursor_anchor.get_position()

            candidates = self.agent_router.generate(text, app_info)

            self.overlay.show_candidates(candidates)
            self.overlay.move_to_cursor(cursor_pos)
        except Exception as e:
            print(f"Error in on_voice_input: {e}")

    def on_clipboard_input(self, text):
        """处理剪贴板输入"""
        try:
            app_info = self.app_detector.detect()
            self.current_context = app_info
            cursor_pos = self.cursor_anchor.get_position()

            candidates = self.agent_router.generate(text, app_info)

            self.overlay.show_candidates(candidates)
            self.overlay.move_to_cursor(cursor_pos)
        except Exception as e:
            print(f"Error in on_clipboard_input: {e}")

    def run(self):
        """运行助手"""
        try:
            print("Starting AI Input Assistant...")

            # 启动输入监听器
            self.keyboard.start()
            self.voice.start()
            self.clipboard.start()

            print("AI Input Assistant is running. Press Ctrl+C to exit.")
            print("Start typing to see suggestions...")

        except Exception as e:
            print(f"Error starting assistant: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    assistant = AIInputAssistant()
    assistant.run()
    sys.exit(app.exec())