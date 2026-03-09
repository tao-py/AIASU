from typing import List, Dict, Any
from Ui.base import CandidateItem

class CodeAgent:

    def __init__(self):
        # 代码补全模板库
        self.snippets = {
            "python": {
                "function": [
                    "def function_name(params):\n    \"\"\"\n    Description\n    \"\"\"\n    pass",
                    "def __init__(self):\n    super().__init__()",
                    "@property\n    def name(self):\n        return self._name"
                ],
                "class": [
                    "class ClassName:\n    def __init__(self):\n        pass\n\n    def method(self):\n        pass",
                    "class ChildClass(ParentClass):\n    def __init__(self):\n        super().__init__()"
                ],
                "loop": [
                    "for i in range(10):\n    print(i)",
                    "for item in items:\n    process(item)",
                    "while True:\n    break"
                ],
                "conditional": [
                    "if condition:\n    pass\nelse:\n    pass",
                    "try:\n    pass\nexcept Exception as e:\n    print(f'Error: {e}')",
                    "with context:\n    pass"
                ],
                "import": [
                    "import os\nimport sys",
                    "from typing import List, Dict, Optional",
                    "import numpy as np\nimport pandas as pd"
                ]
            },
            "javascript": {
                "function": [
                    "function functionName(params) {\n  // implementation\n}",
                    "const functionName = (params) => {\n  return result;\n};"
                ],
                "class": [
                    "class ClassName {\n  constructor() {\n    // initialization\n  }\n}",
                    "class ChildClass extends ParentClass {\n  constructor() {\n    super();\n  }\n}"
                ],
                "async": [
                    "async function fetchData() {\n  const response = await fetch(url);\n  return response.json();\n}",
                    "try {\n  const data = await apiCall();\n} catch (error) {\n  console.error(error);\n}"
                ]
            },
            "java": {
                "function": [
                    "public returnType methodName(params) {\n    // implementation\n    return default;\n}",
                    "private void helperMethod() {\n    // helper logic\n}"
                ],
                "class": [
                    "public class ClassName {\n    private String name;\n    \n    public ClassName() {\n        // constructor\n    }\n}",
                    "public class ChildClass extends ParentClass {\n    @Override\n    public void method() {\n        super.method();\n    }\n}"
                ]
            },
            "cpp": {
                "function": [
                    "type function_name(params) {\n    // implementation\n    return default_value;\n}",
                    "void function_name() {\n    // no return\n}"
                ],
                "class": [
                    "class ClassName {\npublic:\n    ClassName();\n    ~ClassName();\n    void method();\nprivate:\n    int member;\n};"
                ]
            }
        }

        # 通用代码模式
        self.common_patterns = {
            "print": ["print('Hello, World!')", "print(f'Value: {variable}')", "console.log('Hello, World!')"],
            "main": [
                "if __name__ == '__main__':\n    main()",
                "public static void main(String[] args) {\n    // entry point\n}"
            ],
            "return": ["return result", "return True", "return None"]
        }

    def run(self, text: str, context: Dict[str, Any] = None) -> List[str]:
        """生成代码补全候选"""
        candidates = []
        language = self._detect_language(text, context)

        # 根据语言获取补全
        if language in self.snippets:
            candidates.extend(self._get_language_snippets(language, text))
        else:
            # 通用补全
            candidates.extend(self._get_common_snippets(text))

        # 基于当前文本的智能补全
        text_lower = text.lower().strip()

        # 检测代码模式并提供补全
        if "def " in text_lower or "function " in text_lower:
            candidates.extend(self._complete_function_definition(text, language))
        elif "class " in text_lower:
            candidates.extend(self._complete_class_definition(text, language))
        elif "if " in text_lower:
            candidates.extend(self._complete_conditional(text, language))
        elif "for " in text_lower or "while " in text_lower:
            candidates.extend(self._complete_loop(text, language))
        elif "import " in text_lower or "from " in text_lower:
            candidates.extend(self._complete_import(text, language))

        # 去重并限制数量
        unique_candidates = list(set(candidates))[:6]

        # 添加分数
        scored_candidates = []
        for candidate in unique_candidates:
            score = 0.6 if language == "unknown" else 0.8
            scored_candidates.append(
                CandidateItem(
                    text=candidate,
                    score=score,
                    metadata={"agent": "code", "language": language}
                )
            )

        return scored_candidates

    def _detect_language(self, text: str, context: Dict[str, Any] = None) -> str:
        """检测编程语言"""
        if context:
            app_type = context.get("type", "")
            if app_type in ["editor", "ide"]:
                # 从文件扩展名检测
                file_path = context.get("file_path", "")
                if file_path:
                    ext = file_path.split('.')[-1].lower()
                    ext_map = {
                        "py": "python", "js": "javascript", "ts": "typescript",
                        "java": "java", "cpp": "cpp", "c": "c", "cs": "csharp",
                        "go": "go", "rs": "rust", "rb": "ruby", "php": "php",
                        "swift": "swift", "kt": "kotlin", "scala": "scala"
                    }
                    return ext_map.get(ext, "unknown")

        # 基于语法特征检测
        text_lower = text.lower()
        if "def " in text_lower or "import " in text_lower or "from " in text_lower:
            return "python"
        elif "function " in text_lower or "const " in text_lower or "let " in text_lower:
            return "javascript"
        elif "public class" in text_lower or "public static void" in text_lower:
            return "java"
        elif "#include" in text_lower or "int main" in text_lower:
            return "cpp"

        return "unknown"

    def _get_language_snippets(self, language: str, text: str) -> List[str]:
        """获取语言特定片段"""
        snippets = []
        if language in self.snippets:
            lang_snippets = self.snippets[language]

            # 随机选择一些片段
            for category in ["function", "class", "loop", "conditional"]:
                if category in lang_snippets:
                    snippets.extend(lang_snippets[category][:2])

        return snippets[:5]

    def _get_common_snippets(self, text: str) -> List[str]:
        """获取通用片段"""
        snippets = []
        for key in ["print", "main", "return"]:
            snippets.extend(self.common_patterns[key][:2])
        return snippets

    def _complete_function_definition(self, text: str, language: str) -> List[str]:
        """补全函数定义"""
        completions = []
        if language == "python":
            completions = [
                f"{text.rstrip()}\n    pass",
                f"{text.rstrip()}\n    \"\"\"\n    TODO: implement\n    \"\"\"\n    pass",
                f"{text.rstrip()}\n    return None"
            ]
        elif language in ["javascript", "typescript"]:
            completions = [
                f"{text.rstrip()} {{\n  // implementation\n  return;\n}}",
                f"{text.rstrip()} {{\n  throw new Error('Not implemented');\n}}"
            ]
        return completions

    def _complete_class_definition(self, text: str, language: str) -> List[str]:
        """补全类定义"""
        completions = []
        if language == "python":
            completions = [
                f"{text.rstrip()}:\n    def __init__(self):\n        pass\n\n    def method(self):\n        pass",
                f"{text.rstrip()}:\n    pass"
            ]
        return completions

    def _complete_conditional(self, text: str, language: str) -> List[str]:
        """补全条件语句"""
        return [
            f"{text.rstrip()}\n    pass\nelse:\n    pass",
            f"{text.rstrip()}\n    # handle true case\nelse:\n    # handle false case"
        ]

    def _complete_loop(self, text: str, language: str) -> List[str]:
        """补全循环"""
        return [
            f"{text.rstrip()}\n    break",
            f"{text.rstrip()}\n    continue",
            f"{text.rstrip()}\n    print('loop')"
        ]

    def _complete_import(self, text: str, language: str) -> List[str]:
        """补全导入语句"""
        if language == "python":
            return [
                f"{text.rstrip()}",
                f"{text.rstrip()} as ",
                f"{text.rstrip()} import "
            ]
        return []