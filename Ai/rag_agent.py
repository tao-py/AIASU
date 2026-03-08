from Knowledge.rag_engine import RagEngine

class RagAgent:

    def __init__(self):

        self.rag = RagEngine()

    def run(self, text):

        return self.rag.query(text)