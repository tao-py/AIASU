from PySide6.QtCore import QPropertyAnimation


class AnimationEngine:

    def fade_in(self, widget):

        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(120)
        anim.setStartValue(0)
        anim.setEndValue(1)

        anim.start()

    def fade_out(self, widget):

        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(100)
        anim.setStartValue(1)
        anim.setEndValue(0)

        anim.start()