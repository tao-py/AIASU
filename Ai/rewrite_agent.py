import random
from typing import List, Dict, Any
from Ui.base import CandidateItem

class RewriteAgent:

    def __init__(self):
        # 改写策略库
        self.rewrite_strategies = {
            "formal": [
                lambda t: t[0].upper() + t[1:] if t else t,
                lambda t: t + " accordingly.",
                lambda t: "It is important to note that " + t.lower()
            ],
            "concise": [
                lambda t: self._remove_redundant_words(t),
                lambda t: self._simplify_sentence(t),
                lambda t: t.replace("in order to", "to").replace("due to the fact that", "because")
            ],
            "emphatic": [
                lambda t: t + " This is crucial.",
                lambda t: "Most importantly, " + t.lower(),
                lambda t: t + " without exception."
            ],
            "polite": [
                lambda t: "Would you mind " + t.lower() if t.startswith("Please") else t,
                lambda t: "I would appreciate it if you could " + t.lower(),
                lambda t: "If possible, " + t.lower()
            ],
            "professional": [
                lambda t: "Per your request, " + t[0].lower() + t[1:] if t else t,
                lambda t: "In accordance with " + t.lower(),
                lambda t: "For your consideration: " + t
            ]
        }

    def run(self, text: str, context: Dict[str, Any] = None) -> List[CandidateItem]:
        """生成文本改写候选"""
        candidates = []

        # 选择改写策略
        text_lower = text.lower().strip()

        # 根据文本类型选择策略
        if any(word in text_lower for word in ["please", "kindly", "could you", "would you"]):
            strategies = ["formal", "professional"]
        elif len(text.split()) > 20:
            strategies = ["concise"]
        elif text.endswith("?") or text.endswith("？"):
            strategies = ["polite", "professional"]
        else:
            strategies = ["formal", "concise", "emphatic", "professional"]

        # 应用改写策略
        for strategy in strategies:
            if strategy in self.rewrite_strategies:
                for transformer in self.rewrite_strategies[strategy][:2]:
                    try:
                        rewritten = transformer(text)
                        if rewritten and rewritten != text and len(rewritten) > 0:
                            candidates.append(
                                CandidateItem(
                                    text=rewritten,
                                    score=0.7,
                                    metadata={"agent": "rewrite", "strategy": strategy}
                                )
                            )
                    except:
                        continue

        # 添加基本变体
        basic_variants = [
            text.capitalize(),
            text.lower() if text[0].isupper() else text,
            text + "." if not text.endswith((".", "!", "?")) else text,
            text.rstrip(".!?") + "."
        ]

        for variant in basic_variants:
            if variant != text:
                candidates.append(
                    CandidateItem(
                        text=variant,
                        score=0.5,
                        metadata={"agent": "rewrite", "strategy": "basic"}
                    )
                )

        # 去重
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c.text not in seen:
                seen.add(c.text)
                unique_candidates.append(c)

        return unique_candidates[:5]

    def _remove_redundant_words(self, text: str) -> str:
        """移除冗余词语"""
        redundant_phrases = [
            ("in order to", "to"),
            ("due to the fact that", "because"),
            ("at this point in time", "now"),
            ("in the event that", "if"),
            ("for the purpose of", "for"),
            ("with regard to", "regarding"),
            ("in the near future", "soon"),
            ("in my opinion", ""),
            ("I think that", ""),
            ("it is important to note that", ""),
        ]

        result = text
        for redundant, replacement in redundant_phrases:
            result = result.replace(redundant, replacement)
        return result.strip()

    def _simplify_sentence(self, text: str) -> str:
        """简化句子"""
        # 移除不必要的修饰词
        words = text.split()
        if len(words) > 5:
            # 简单处理：移除一些填充词
            fillers = ["actually", "basically", "literally", "virtually", "practically"]
            words = [w for w in words if w.lower() not in fillers]
            return " ".join(words)
        return text