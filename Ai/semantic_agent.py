import random
from typing import List, Dict, Any
import re

from Ui.base import CandidateItem

class SemanticAgent:

    def __init__(self):
        # 常见短语补全模板
        self.phrase_templates = {
            "default": [
                "Furthermore, it is important to note that",
                "In addition to this,",
                "As a result,",
                "Consequently,",
                "However,",
                "On the other hand,",
                "For instance,",
                "To illustrate this point,",
                "In conclusion,",
                "To summarize,"
            ],
            "question": [
                "Could you please clarify",
                "I would like to understand",
                "What are the implications of",
                "How does this relate to",
                "Why is this important?"
            ],
            "agreement": [
                "I completely agree with",
                "That's a valid point about",
                "I see your perspective on",
                "You're absolutely right that",
                "That makes perfect sense given"
            ],
            "disagreement": [
                "I see it differently regarding",
                "With all due respect, I think",
                "I'm not sure I agree that",
                "From my perspective,",
                "An alternative viewpoint would be"
            ]
        }

        # 领域特定补全
        self.domain_specific = {
            "editor": [
                "The function should be refactored to",
                "Consider adding error handling for",
                "This code could be optimized by",
                "It would be better to implement",
                "A more efficient approach would be"
            ],
            "browser": [
                "This webpage provides information about",
                "The main topic discussed here is",
                "Key points from this source:",
                "According to this article,",
                "The author argues that"
            ],
            "office": [
                "Regarding the meeting agenda,",
                "For the project status,",
                "In response to your email,",
                "Attached please find",
                "Following up on our discussion,"
            ]
        }

    def run(self, text: str, context: Dict[str, Any] = None) -> List[CandidateItem]:
        """生成语义补全候选"""
        candidates = []

        # 分析文本类型
        text_type = self._analyze_text_type(text)

        # 添加基于类型的模板补全
        if text_type in self.phrase_templates:
            templates = self.phrase_templates[text_type]
            for template in random.sample(templates, min(3, len(templates))):
                candidates.append(f"{text} {template.lower()}")

        # 添加领域特定补全
        app_type = context.get("type", "general") if context else "general"
        if app_type in self.domain_specific:
            domain_templates = self.domain_specific[app_type]
            for template in random.sample(domain_templates, min(2, len(domain_templates))):
                candidates.append(f"{text}, {template.lower()}")

        # 添加续写补全（基于文本结尾）
        if text.endswith((".", "!", "?", "。")):
            # 对于完整句子，提供承接语句
            completions = [
                f"{text} This suggests that",
                f"{text} Therefore,",
                f"{text} In other words,",
                f"{text} For example,"
            ]
            candidates.extend(completions[:2])

        # 确保有足够的候选
        if len(candidates) < 3:
            candidates.extend([
                f"{text} ...",
                f"{text} and",
                f"{text} or"
            ])

        # 去重并限制数量
        unique_candidates = list(set(candidates))[:5]

        # 为候选添加分数
        scored_candidates = []
        for i, candidate in enumerate(unique_candidates):
            # 简单的评分：基于长度和类型匹配
            score = 0.5 + (len(candidate) / 200)  # 基础分
            if text_type in candidate.lower():
                score += 0.3
            scored_candidates.append(
                CandidateItem(
                    text=candidate,
                    score=min(1.0, score),
                    metadata={"agent": "semantic", "type": text_type}
                )
            )

        return scored_candidates

    def _analyze_text_type(self, text: str) -> str:
        """分析文本类型"""
        text_lower = text.lower().strip()

        # 问题检测
        if text.endswith("?") or text_lower.startswith(("what", "how", "why", "when", "where", "who", "can you", "could you")):
            return "question"

        # 同意检测
        agreement_words = ["yes", "agree", "correct", "right", "exactly", "indeed", "absolutely"]
        if any(word in text_lower for word in agreement_words):
            return "agreement"

        # 不同意检测
        disagreement_words = ["but", "however", "disagree", "not sure", "different", "however"]
        if any(word in text_lower for word in disagreement_words):
            return "disagreement"

        return "default"