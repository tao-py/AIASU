from Ui.ime_window import IMEWindow


class OverlayWindow:

    def __init__(self):

        self.ime = IMEWindow()

    def show_candidates(self, candidates):

        self.ime.update_candidates(candidates)

    def hide(self):

        self.ime.hide()