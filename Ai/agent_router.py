from Ai.semantic_agent import SemanticAgent
from Ai.code_agent import CodeAgent
from Ai.rag_agent import RagAgent
from Ai.rewrite_agent import RewriteAgent
from Ai.candidate_ranker import CandidateRanker

class AgentRouter:

    def __init__(self):

        self.semantic = SemanticAgent()
        self.code = CodeAgent()
        self.rag = RagAgent()
        self.rewrite = RewriteAgent()

        self.rank = CandidateRanker()

    def generate(self, text, app):

        candidates = []

        candidates += self.semantic.run(text)

        if "code" in app.lower():
            candidates += self.code.run(text)

        candidates += self.rag.run(text)

        candidates += self.rewrite.run(text)

        return self.rank.rank(candidates)