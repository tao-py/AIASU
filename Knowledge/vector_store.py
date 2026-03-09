"""
简单的向量存储实现，使用numpy和pickle进行持久化
不依赖chromadb和onnxruntime
"""

import numpy as np
import pickle
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class SimpleVectorStore:

    def __init__(self, store_path: str = "./data/vector_store.pkl"):
        self.store_path = store_path
        self.documents = []  # 文档列表
        self.embeddings = []  # embedding数组
        self.metadatas = []  # 元数据列表
        self._load()

    def _load(self):
        """从磁盘加载数据"""
        try:
            if os.path.exists(self.store_path):
                with open(self.store_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.embeddings = data.get('embeddings', [])
                    self.metadatas = data.get('metadatas', [])
                print(f"Loaded vector store with {len(self.documents)} documents")
            else:
                os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
                print("Created new vector store")
        except Exception as e:
            print(f"Error loading vector store: {e}")
            self.documents = []
            self.embeddings = []
            self.metadatas = []

    def _save(self):
        """保存到磁盘"""
        try:
            data = {
                'documents': self.documents,
                'embeddings': self.embeddings,
                'metadatas': self.metadatas,
                'updated_at': datetime.now()
            }
            with open(self.store_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Error saving vector store: {e}")

    def add(self, text: str, embedding: List[float], metadata: Dict[str, Any] = None):
        """添加文档"""
        try:
            self.documents.append(text)
            self.embeddings.append(np.array(embedding))
            self.metadatas.append(metadata or {})
            self._save()
            return True
        except Exception as e:
            print(f"VectorStore add error: {e}")
            return False

    def search(self, query_embedding: List[float], n_results: int = 3, 
               where: Dict[str, Any] = None) -> Dict[str, List]:
        """搜索最相似的文档"""
        try:
            if not self.documents:
                return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

            query_vec = np.array(query_embedding)
            
            # 计算余弦相似度
            similarities = []
            for emb in self.embeddings:
                sim = self._cosine_similarity(query_vec, emb)
                similarities.append(sim)
            
            # 排序并获取top n
            indices = np.argsort(similarities)[::-1][:n_results]
            
            results = {
                "documents": [[self.documents[i] for i in indices]],
                "metadatas": [[self.metadatas[i] for i in indices]],
                "distances": [[1 - similarities[i] for i in indices]]  # 转换为距离
            }
            
            return results
        except Exception as e:
            print(f"VectorStore search error: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    def count(self) -> int:
        """获取文档数量"""
        return len(self.documents)

    def clear(self) -> bool:
        """清空所有文档"""
        try:
            self.documents = []
            self.embeddings = []
            self.metadatas = []
            self._save()
            return True
        except Exception as e:
            print(f"VectorStore clear error: {e}")
            return False

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


# 为了向后兼容，保留VectorStore名称
VectorStore = SimpleVectorStore