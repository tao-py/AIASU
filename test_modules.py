#!/usr/bin/env python
"""
测试脚本 - 验证AIASU各个模块的功能
"""

import sys
from PySide6.QtWidgets import QApplication

# 测试各个模块
def test_modules():
    print("=" * 60)
    print("AIASU 模块功能测试")
    print("=" * 60)

    # 1. 测试Context模块
    print("\n1. 测试 Context 模块")
    try:
        from Context.app_detector import AppDetector
        detector = AppDetector()
        app_info = detector.detect()
        print(f"   ✓ AppDetector 工作正常")
        print(f"     当前应用: {app_info.get('name')}")
        print(f"     应用类型: {app_info.get('type')}")
    except Exception as e:
        print(f"   ✗ AppDetector 错误: {e}")

    # 2. 测试Platform模块
    print("\n2. 测试 Platform 模块")
    try:
        from Platform.cursor_anchor import CursorAnchor
        cursor = CursorAnchor()
        pos = cursor.get_position()
        print(f"   ✓ CursorAnchor 工作正常")
        print(f"     光标位置: ({pos.x}, {pos.y})")
    except Exception as e:
        print(f"   ✗ CursorAnchor 错误: {e}")

    # 3. 测试Knowledge模块
    print("\n3. 测试 Knowledge 模块")
    try:
        from Knowledge.embedding import embed
        from Knowledge.rag_engine import RagEngine

        # 测试embedding
        test_text = "这是一个测试文本"
        embedding = embed(test_text)
        print(f"   ✓ Embedding 工作正常")
        print(f"     向量维度: {embedding.shape}")

        # 测试RAG
        rag = RagEngine()
        rag.add_document("测试文档1", {"source": "test1"})
        rag.add_document("测试文档2", {"source": "test2"})
        results = rag.query("测试")
        print(f"   ✓ RAG 工作正常")
        print(f"     查询结果数量: {len(results)}")
        print(f"     文档总数: {rag.get_document_count()}")
    except Exception as e:
        print(f"   ✗ Knowledge 模块错误: {e}")

    # 4. 测试AI模块
    print("\n4. 测试 AI 模块")
    try:
        from Ai.semantic_agent import SemanticAgent
        from Ai.code_agent import CodeAgent
        from Ai.rewrite_agent import RewriteAgent
        from Ai.candidate_ranker import CandidateRanker

        # 测试SemanticAgent
        semantic = SemanticAgent()
        candidates = semantic.run("这是一个测试", {"type": "general"})
        print(f"   ✓ SemanticAgent 工作正常")
        print(f"     生成候选数: {len(candidates)}")

        # 测试CodeAgent
        code = CodeAgent()
        candidates = code.run("def test():", {"type": "editor", "file_path": "test.py"})
        print(f"   ✓ CodeAgent 工作正常")
        print(f"     生成候选数: {len(candidates)}")

        # 测试RewriteAgent
        rewrite = RewriteAgent()
        candidates = rewrite.run("这是一个需要改写的句子")
        print(f"   ✓ RewriteAgent 工作正常")
        print(f"     生成候选数: {len(candidates)}")

        # 测试CandidateRanker
        ranker = CandidateRanker()
        from Ui.base import CandidateItem
        test_candidates = [
            CandidateItem(text="候选1", score=0.8),
            CandidateItem(text="候选2", score=0.6),
            CandidateItem(text="候选3", score=0.9)
        ]
        ranked = ranker.rank(test_candidates, query="测试")
        print(f"   ✓ CandidateRanker 工作正常")
        print(f"     排序后候选数: {len(ranked)}")
    except Exception as e:
        print(f"   ✗ AI 模块错误: {e}")

    # 5. 测试AgentRouter
    print("\n5. 测试 AgentRouter 模块")
    try:
        from Ai.agent_router import AgentRouter
        router = AgentRouter()
        candidates = router.generate("这是一个测试", {"type": "general"})
        print(f"   ✓ AgentRouter 工作正常")
        print(f"     生成候选总数: {len(candidates)}")
        for i, c in enumerate(candidates[:3], 1):
            print(f"     候选{i}: {c.text[:50]}...")
    except Exception as e:
        print(f"   ✗ AgentRouter 错误: {e}")

    # 6. 测试Inputs模块
    print("\n6. 测试 Inputs 模块")
    try:
        from Inputs.keyboard_listener import KeyboardListener
        from Inputs.voice_input import VoiceInput
        from Inputs.clipboard_monitor import ClipboardMonitor

        print("   ✓ 所有Inputs模块导入成功")
        print("     注意: keyboard_listener, voice_input, clipboard_monitor 需要实际交互才能完整测试")
    except Exception as e:
        print(f"   ✗ Inputs 模块错误: {e}")

    # 7. 测试UI模块（需要QApplication）
    print("\n7. 测试 UI 模块")
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        from Ui.overlay_window import OverlayWindow
        from Ui.candidate_view import CandidateView

        # 测试OverlayWindow
        overlay = OverlayWindow()
        print("   ✓ OverlayWindow 创建成功")

        # 测试CandidateView
        candidate_view = CandidateView()
        print("   ✓ CandidateView 创建成功")

        print("   ✓ UI 模块基本功能正常")
    except Exception as e:
        print(f"   ✗ UI 模块错误: {e}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_modules()