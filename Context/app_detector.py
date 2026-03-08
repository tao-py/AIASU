import psutil

class AppDetector:

    def detect(self):

        try:
            return psutil.Process().name()
        except:
            return "unknown"