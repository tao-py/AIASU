import rumps
import threading
import main

class MenuBarApp(rumps.App):

    def __init__(self):

        super().__init__("AI")

        self.menu = [
            "Enable",
            "Disable",
            "Quit"
        ]

    @rumps.clicked("Enable")
    def enable(self, _):
        threading.Thread(target=main.start).start()

    @rumps.clicked("Quit")
    def quit(self, _):
        rumps.quit_application()

def start():

    MenuBarApp().run()