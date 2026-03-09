import numpy as np
from typing import List, Dict, Any
from Knowledge.embedding import embed
from Ui.base import CandidateItem

class CandidateRanker:

    def __init__(self):
        self.embedding_cache = {}

    def rank(self, candidates: List[CandidateItem], query: str = None) -> List[CandidateItem]:
        """对候选进行排序"""
        if not candidates:
            return []

        # 如果没有查询文本，返回原始顺序
        if not query:
            return sorted(candidates, key=lambda x: x.score, reverse=True)

        try:
            # 计算查询的embedding
            query_embedding = embed(query)
            if isinstance(query_embedding, list):
                query_embedding = np.array(query_embedding)
            elif hasattr(query_embedding, 'cpu'):
                query_embedding = query_embedding.cpu().numpy()

            # 计算每个候选的embedding和相似度
            scored_candidates = []
            for candidate in candidates:
                candidate_text = candidate.text

                # 检查缓存
                if candidate_text in self.embedding_cache:
                    candidate_embedding = self.embedding_cache[candidate_text]
                else:
                    candidate_embedding = embed(candidate_text)
                    if isinstance(candidate_embedding, list):
                        candidate_embedding = np.array(candidate_embedding)
                    elif hasattr(candidate_embedding, 'cpu'):
                        candidate_embedding = candidate_embedding.cpu().numpy()
                    self.embedding_cache[candidate_text] = candidate_embedding

                # 计算余弦相似度
                similarity = self._cosine_similarity(query_embedding, candidate_embedding)

                # 结合原始分数和相似度分数
                final_score = 0.3 * candidate.score + 0.7 * similarity

                # 创建新的候选项（保持元数据）
                new_candidate = CandidateItem(
                    text=candidate.text,
                    description=candidate.description,
                    icon=candidate.icon,
                    score=final_score,
                    metadata=candidate.metadata
                )
                scored_candidates.append(new_candidate)

            # 按分数降序排序
            scored_candidates.sort(key=lambda x: x.score, reverse=True)

            return scored_candidates[:5]

        except Exception as e:
            print(f"Ranking error: {e}")
            # 出错时返回原始排序
            return sorted(candidates, key=lambda x: x.score, reverse=True)[:5]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """计算余弦相似度"""
        try:
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)

            if norm_a == 0 or norm_b == 0:
                return 0.0

            return float(np.dot(a, b) / (norm_a * norm_b))
        except:
            return 0.0

    def clear_cache(self):
        """清空embedding缓存"""
        self.embedding_cache.clear()