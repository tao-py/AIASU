from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer

from Ui.candidate_view import CandidateView
from Ui.animation_engine import AnimationEngine
from Platform.cursor_anchor import CursorAnchor


class IMEWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.cursor = CursorAnchor()

        self.anim = AnimationEngine()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.NoFocus)

        self.view = CandidateView()

        layout = QVBoxLayout()
        layout.addWidget(self.view)

        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.follow_cursor)
        self.timer.start(16)

    def follow_cursor(self):

        x, y = self.cursor.get_position()

        self.move(x + 10, y + 25)

    def update_candidates(self, candidates):

        if not candidates:
            self.hide()
            return

        self.view.update_candidates(candidates)

        if not self.isVisible():
            self.anim.fade_in(self)

        self.show()