from Knowledge.embedding import embed
from Knowledge.vector_store import VectorStore

class RagEngine:

    def __init__(self):
        self.vector_store = VectorStore()
        self._initialized = False

    def query(self, text: str, n_results: int = 3):
        """查询相关文档"""
        try:
            # 使用query_text进行搜索（由VectorStore的embedding_function处理）
            results = self.vector_store.search(text, n_results=n_results)

            # 提取文档
            documents = results.get("documents", [[]])[0]

            return documents if documents else ["No relevant documents found."]
        except Exception as e:
            print(f"RAG query error: {e}")
            return ["Error retrieving documents."]

    def add_document(self, text: str, metadata: dict = None):
        """添加文档到知识库"""
        try:
            # VectorStore会自动调用embedding_function
            success = self.vector_store.add(text, None, metadata)
            return success
        except Exception as e:
            print(f"RAG add document error: {e}")
            return False

    def get_document_count(self):
        """获取文档数量"""
        return self.vector_store.count()