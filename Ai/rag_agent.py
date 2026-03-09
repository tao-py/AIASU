from Knowledge.rag_engine import RagEngine
from Ui.base import CandidateItem
from typing import List

class RagAgent:

    def __init__(self):
        self.rag = RagEngine()

    def run(self, text: str) -> List[CandidateItem]:
        """运行RAG查询"""
        try:
            documents = self.rag.query(text)
            candidates = []
            for doc in documents:
                if doc and isinstance(doc, str):
                    candidates.append(
                        CandidateItem(
                            text=doc[:100],  # 限制长度
                            score=0.7,  # RAG文档的默认分数
                            metadata={"agent": "rag", "source": "knowledge_base"}
                        )
                    )
            return candidates[:3]  # 最多返回3个
        except Exception as e:
            print(f"RAG agent error: {e}")
            return []