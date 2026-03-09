"""
编辑器上下文检测模块
"""

class EditorContext:

    def __init__(self):
        self.context_cache = {}

    def get_context(self, file_path=None, language=None, cursor_position=None):
        """获取编辑器上下文信息"""
        context = {
            "type": "editor",
            "file_path": file_path,
            "language": language or self._detect_language(file_path),
            "cursor_position": cursor_position,
            "surrounding_code": "",
            "imports": [],
            "functions": [],
            "variables": []
        }

        # 如果有文件路径，尝试读取文件
        if file_path:
            context.update(self._analyze_file(file_path, cursor_position))

        return context

    def _detect_language(self, file_path):
        """根据文件扩展名检测语言"""
        if not file_path:
            return "unknown"

        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".less": "less",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
            ".sql": "sql",
            ".sh": "bash",
            ".ps1": "powershell",
            ".r": "r",
            ".m": "matlab",
            ".pl": "perl",
            ".lua": "lua",
            ".vim": "vim",
        }

        import os
        ext = os.path.splitext(file_path)[1].lower()
        return ext_map.get(ext, "unknown")

    def _analyze_file(self, file_path, cursor_position):
        """分析文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            if cursor_position:
                # cursor_position 可能是行号或 (行,列)
                if isinstance(cursor_position, int):
                    line_idx = min(cursor_position - 1, len(lines) - 1)
                else:
                    line_idx = min(cursor_position[0] - 1, len(lines) - 1)

                # 获取前后文
                start = max(0, line_idx - 5)
                end = min(len(lines), line_idx + 5)
                surrounding = '\n'.join(lines[start:end])
            else:
                surrounding = content[:500]  # 取前500字符

            return {
                "surrounding_code": surrounding,
                "total_lines": len(lines),
                "file_size": len(content)
            }
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
            return {}