from Knowledge.embedding import embed
from Knowledge.vector_store import search

class RagEngine:

    def query(self, text):

        e = embed(text)

        results = search(e)

        return results["documents"][0]