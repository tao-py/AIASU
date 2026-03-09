"""
文档索引器 - 用于将文档添加到RAG知识库
"""

import os
from pathlib import Path
from typing import List, Optional
from Knowledge.rag_engine import RagEngine

class DocumentIndexer:

    def __init__(self, rag_engine: RagEngine = None):
        self.rag_engine = rag_engine or RagEngine()
        self.supported_extensions = {
            '.txt': self._process_text,
            '.md': self._process_text,
            '.py': self._process_code,
            '.js': self._process_code,
            '.ts': self._process_code,
            '.java': self._process_code,
            '.cpp': self._process_code,
            '.c': self._process_code,
            '.cs': self._process_code,
            '.go': self._process_code,
            '.rs': self._process_code,
            '.rb': self._process_code,
            '.php': self._process_code,
            '.html': self._process_code,
            '.css': self._process_code,
            '.json': self._process_json,
            '.xml': self._process_text,
            '.csv': self._process_text,
        }

    def index_file(self, file_path: str, metadata: dict = None) -> bool:
        """索引单个文件"""
        try:
            path = Path(file_path)

            if not path.exists():
                print(f"File not found: {file_path}")
                return False

            ext = path.suffix.lower()
            if ext not in self.supported_extensions:
                print(f"Unsupported file type: {ext}")
                return False

            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 处理文件内容
            processor = self.supported_extensions[ext]
            documents = processor(content, file_path)

            # 添加到知识库
            success = True
            for doc in documents:
                if doc.strip():
                    meta = metadata.copy() if metadata else {}
                    meta.update({
                        'source': file_path,
                        'type': ext.replace('.', ''),
                        'size': len(content)
                    })
                    if not self.rag_engine.add_document(doc, meta):
                        success = False

            if success:
                print(f"Indexed {len(documents)} document(s) from {file_path}")
            return success

        except Exception as e:
            print(f"Error indexing file {file_path}: {e}")
            return False

    def index_directory(self, directory: str, recursive: bool = True, 
                        max_files: int = 100) -> int:
        """索引目录中的所有支持文件"""
        indexed_count = 0
        path = Path(directory)

        if not path.exists():
            print(f"Directory not found: {directory}")
            return 0

        # 获取所有文件
        if recursive:
            files = list(path.rglob('*'))
        else:
            files = list(path.glob('*'))

        # 过滤支持的文件类型
        supported_files = [
            f for f in files 
            if f.is_file() and f.suffix.lower() in self.supported_extensions
        ][:max_files]

        print(f"Found {len(supported_files)} files to index")

        for file_path in supported_files:
            if self.index_file(str(file_path)):
                indexed_count += 1

        print(f"Successfully indexed {indexed_count}/{len(supported_files)} files")
        return indexed_count

    def index_text(self, text: str, metadata: dict = None) -> bool:
        """索引原始文本"""
        try:
            # 将文本分块
            chunks = self._chunk_text(text, chunk_size=500, overlap=50)

            success = True
            for chunk in chunks:
                if chunk.strip():
                    if not self.rag_engine.add_document(chunk, metadata):
                        success = False

            if success:
                print(f"Indexed {len(chunks)} text chunks")
            return success
        except Exception as e:
            print(f"Error indexing text: {e}")
            return False

    def _process_text(self, content: str, file_path: str) -> List[str]:
        """处理文本文件"""
        return self._chunk_text(content, 500, 50)

    def _process_code(self, content: str, file_path: str) -> List[str]:
        """处理代码文件 - 按函数/类分割"""
        # 简单实现：按行分块
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0

        for line in lines:
            current_chunk.append(line)
            current_size += len(line)

            if current_size >= 500:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0

        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks if chunks else [content]

    def _process_json(self, content: str, file_path: str) -> List[str]:
        """处理JSON文件"""
        # 对于JSON，整个文件作为一个文档
        return [content]

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """将文本分块"""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)

            # 尝试在句子边界处分割
            if end < text_len:
                # 查找最近的句号、问号或换行符
                for sep in ['. ', '.\n', '? ', '?\n', '\n\n']:
                    pos = text.rfind(sep, start, end)
                    if pos > start + chunk_size // 2:
                        end = pos + len(sep)
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap if end < text_len else text_len

        return chunks