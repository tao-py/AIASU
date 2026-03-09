from Ai.semantic_agent import SemanticAgent
from Ai.code_agent import CodeAgent
from Ai.rag_agent import RagAgent
from Ai.rewrite_agent import RewriteAgent
from Ai.candidate_ranker import CandidateRanker
from typing import List, Dict, Any

class AgentRouter:

    def __init__(self):
        self.semantic = SemanticAgent()
        self.code = CodeAgent()
        self.rag = RagAgent()
        self.rewrite = RewriteAgent()
        self.rank = CandidateRanker()

    def generate(self, text: str, app: Dict[str, Any]) -> List:
        """生成候选列表"""
        candidates = []

        # 语义补全
        try:
            semantic_candidates = self.semantic.run(text, app)
            candidates.extend(semantic_candidates)
        except Exception as e:
            print(f"Semantic agent error: {e}")

        # 代码补全（如果是编辑器或IDE）
        app_type = app.get("type", "") if isinstance(app, dict) else str(app).lower()
        if "editor" in app_type or "ide" in app_type or "code" in app_type:
            try:
                code_candidates = self.code.run(text, app)
                candidates.extend(code_candidates)
            except Exception as e:
                print(f"Code agent error: {e}")

        # RAG知识补全
        try:
            rag_candidates = self.rag.run(text)
            candidates.extend(rag_candidates)
        except Exception as e:
            print(f"RAG agent error: {e}")

        # 文本改写
        try:
            rewrite_candidates = self.rewrite.run(text, app)
            candidates.extend(rewrite_candidates)
        except Exception as e:
            print(f"Rewrite agent error: {e}")

        # 去重并排序
        if candidates:
            # 使用CandidateRanker排序，传入查询文本
            ranked = self.rank.rank(candidates, query=text)
            return ranked[:5]  # 返回前5个

        return []