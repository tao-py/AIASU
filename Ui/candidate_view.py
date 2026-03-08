from PySide6.QtWidgets import QListWidget
from PySide6.QtCore import Qt


class CandidateView(QListWidget):

    def __init__(self):

        super().__init__()

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.setStyleSheet("""
        QListWidget {
            background: rgba(28,28,30,230);
            border-radius: 10px;
            padding: 6px;
            color: white;
            font-size: 14px;
        }

        QListWidget::item {
            padding: 6px;
        }

        QListWidget::item:selected {
            background: rgba(80,120,255,180);
        }
        """)

    def update_candidates(self, candidates):

        self.clear()

        for c in candidates:
            self.addItem(c)