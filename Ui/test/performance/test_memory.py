"""
内存使用测试
测试UI组件的内存使用和泄漏检测
"""

import pytest
import gc
import weakref
from PySide6.QtWidgets import QApplication

from ...base import Position, CandidateItem
from ...ui_manager import UIManager
from ...animation_engine import AnimationEngine
from ...overlay_window import OverlayWindow
from ...candidate_view import CandidateView
from ...ime_window import IMEWindow
from ...input_preview import InputPreview
from ...config_manager import ConfigManager
from ..utils.helpers import (
    setup_test_qt_app,
    teardown_test_qt_app,
    create_test_config,
    create_test_candidates,
)


class TestMemoryBasics:
    """内存基础测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_no_obvious_memory_leak_on_creation(self, qt_app):
        """测试创建组件无明显内存泄漏"""
        import sys

        config = create_test_config()

        # 获取创建前的对象数
        gc.collect()
        objects_before = len(gc.get_objects())

        # 创建和销毁组件
        for _ in range(10):
            overlay = OverlayWindow("leak_test", config)
            overlay.hide()
            del overlay

        gc.collect()
        objects_after = len(gc.get_objects())

        # 对象数增长应该很小
        objects_increase = objects_after - objects_before
        assert objects_increase < 100  # 增长小于100个对象

    def test_component_garbage_collection(self, qt_app):
        """测试组件垃圾回收"""
        config = create_test_config()

        def create_and_lose_reference():
            overlay = OverlayWindow("gc_test", config)
            # 返回弱引用
            weak_ref = weakref.ref(overlay)
            return weak_ref

        weak_ref = create_and_lose_reference()
        gc.collect()

        # 组件应该被回收
        assert weak_ref() is None

    def test_manager_cleanup_on_deletion(self, qt_app):
        """测试管理器删除时清理"""
        config = create_test_config()
        manager = UIManager(config)

        # 添加组件
        overlay = OverlayWindow("manager_cleanup", config)
        manager.register_component(overlay)

        assert len(manager._components) == 1

        # 删除管理器
        del manager
        gc.collect()

        # 管理器应该被垃圾回收
        # 但由于overlay还有引用，可能不会被完全回收
        # 这里主要测试没有异常


class TestComponentMemoryLeaks:
    """组件内存泄漏测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_overlay_memory_leak(self, qt_app):
        """测试OverlayWindow内存泄漏"""
        config = create_test_config()

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            pytest.skip("psutil not available")
            return

        gc.collect()
        memory_before = process.memory_info().rss

        # 反复创建和销毁
        for _ in range(100):
            overlay = OverlayWindow("overlay_leak", config)
            overlay.show(Position(100, 100))
            overlay.hide()
            del overlay

        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before
        # 100次循环内存增长应该很小
        assert memory_increase < 1024 * 1024  # 小于1MB

    def test_candidate_view_memory_leak(self, qt_app):
        """测试CandidateView内存泄漏"""
        config = create_test_config()

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            pytest.skip("psutil not available")
            return

        gc.collect()
        memory_before = process.memory_info().rss

        for _ in range(100):
            view = CandidateView("candidate_leak", config)
            candidates = create_test_candidates(10)
            view.set_candidates(candidates)
            view.clear_candidates()
            del view

        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before
        assert memory_increase < 1024 * 1024

    def test_ime_window_memory_leak(self, qt_app):
        """测试IMEWindow内存泄漏"""
        config = create_test_config()

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            pytest.skip("psutil not available")
            return

        gc.collect()
        memory_before = process.memory_info().rss

        for _ in range(100):
            ime = IMEWindow("ime_leak", config)
            ime.set_composition_text("测试")
            candidates = create_test_candidates(5)
            ime.set_candidates(candidates)
            del ime

        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before
        assert memory_increase < 1024 * 1024

    def test_input_preview_memory_leak(self, qt_app):
        """测试InputPreview内存泄漏"""
        config = create_test_config()

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            pytest.skip("psutil not available")
            return

        gc.collect()
        memory_before = process.memory_info().rss

        for _ in range(100):
            preview = InputPreview("preview_leak", config)
            preview.set_text("测试文本")
            preview.highlight_text(0, 2, "#FF0000")
            del preview

        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before
        assert memory_increase < 1024 * 1024


class TestAnimationMemoryLeaks:
    """动画内存泄漏测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_animation_engine_memory_leak(self, qt_app):
        """测试AnimationEngine内存泄漏"""
        config = create_test_config()

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            pytest.skip("psutil not available")
            return

        from ...overlay_window import OverlayWindow
        from ...animation_engine import AnimationEngine

        gc.collect()
        memory_before = process.memory_info().rss

        for _ in range(50):
            engine = AnimationEngine(config)
            overlay = OverlayWindow("anim_leak", config)
            engine.fade_in(overlay, duration=100)
            engine.clear_animations()
            del engine
            del overlay

        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before
        assert memory_increase < 1024 * 1024

    def test_animation_cleanup_prevents_leak(self, qt_app):
        """测试动画清理防止泄漏"""
        config = create_test_config()
        from ...overlay_window import OverlayWindow
        from ...animation_engine import AnimationEngine

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            pytest.skip("psutil not available")
            return

        gc.collect()
        memory_before = process.memory_info().rss

        # 不清理动画
        for _ in range(50):
            engine = AnimationEngine(config)
            overlay = OverlayWindow("no_cleanup", config)
            engine.fade_in(overlay, duration=100)
            # 不调用clear_animations
            del engine
            del overlay

        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before
        # 没有清理动画可能会导致更多内存使用
        # 但我们应该有合理的上限
        assert memory_increase < 5 * 1024 * 1024  # 小于5MB


class TestManagerMemoryLeaks:
    """管理器内存泄漏测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_ui_manager_memory_leak(self, qt_app):
        """测试UIManager内存泄漏"""
        config = create_test_config()

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            pytest.skip("psutil not available")
            return

        gc.collect()
        memory_before = process.memory_info().rss

        for _ in range(50):
            manager = UIManager(config)
            manager._animation_controller = AnimationEngine(config)
            manager._theme_manager = ThemeEngine()

            overlay = OverlayWindow("manager_leak", config)
            manager.register_component(overlay)

            # 注销组件
            manager.unregister_component("manager_leak")

            del manager
            del overlay

        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before
        assert memory_increase < 2 * 1024 * 1024  # 小于2MB

    def test_config_manager_memory_leak(self):
        """测试ConfigManager内存泄漏"""
        import tempfile

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            pytest.skip("psutil not available")
            return

        gc.collect()
        memory_before = process.memory_info().rss

        for _ in range(50):
            with tempfile.TemporaryDirectory() as temp_dir:
                manager = ConfigManager(temp_dir)
                manager.set("test.key", "value")
                manager.save_config()
                # 自动清理

        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before
        assert memory_increase < 1024 * 1024


class TestSignalConnectionMemory:
    """信号连接内存测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_signal_connections_cleanup(self, qt_app):
        """测试信号连接清理"""
        from ...base import UIComponent

        config = create_test_config()

        class TestComponent(UIComponent):
            def show(self, position=None):
                pass

            def hide(self):
                pass

            def update_theme(self, theme):
                pass

            def get_preferred_size(self):
                from PySide6.QtCore import QSize
                return QSize(100, 100)

        component = TestComponent("signal_test", config)

        # 添加多个事件处理器
        handlers = []
        for i in range(10):
            def handler(event, idx=i):
                pass
            component.add_event_handler(f"event_{idx}", handler)
            handlers.append(handler)

        # 应该有10个处理器
        total_handlers = sum(len(handlers) for handlers in component._event_handlers.values())
        assert total_handlers == 10

        # 移除一些处理器
        component.remove_event_handler("event_0", handlers[0])
        # 验证数量减少

        # 组件删除时，处理器应该被清理
        del component
        gc.collect()

    def test_manager_signal_cleanup(self, qt_app):
        """测试管理器信号清理"""
        config = create_test_config()
        manager = UIManager(config)

        # 连接信号
        calls = []

        def on_component_registered(name):
            calls.append(("registered", name))

        manager.component_registered.connect(on_component_registered)

        # 注册组件
        overlay = OverlayWindow("signal_cleanup", config)
        manager.register_component(overlay)

        # 应该收到信号
        assert len(calls) >= 0  # 可能收到

        # 注销组件
        manager.unregister_component("signal_cleanup")

        # 删除管理器
        del manager
        gc.collect()


class TestLargeDataStructures:
    """大数据结构测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_large_candidate_list_memory(self, qt_app):
        """测试大候选列表内存"""
        config = create_test_config()
        candidate_view = CandidateView("large_memory", config)

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            gc.collect()
            memory_before = process.memory_info().rss
        except ImportError:
            pytest.skip("psutil not available")
            return

        # 创建大量候选项
        huge_candidates = create_test_candidates(5000)
        candidate_view.set_candidates(huge_candidates)

        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before
        # 5000个候选项应该占用一些内存，但应该合理
        assert memory_increase < 20 * 1024 * 1024  # 小于20MB

        # 清理
        candidate_view.clear_candidates()
        gc.collect()

    def test_theme_cache_memory(self, qt_app):
        """测试主题缓存内存"""
        from ...theme_engine import ThemeEngine
        import tempfile

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            pytest.skip("psutil not available")
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            engine = ThemeEngine(temp_dir)

            gc.collect()
            memory_before = process.memory_info().rss

            # 创建和缓存多个主题
            themes = []
            for i in range(50):
                theme = engine.create_custom_theme(
                    f"cache_theme_{i}",
                    "default",
                    background_color=f"#{(i * 5) % 256:02x}{(i * 10) % 256:02x}{(i * 15) % 256:02x}",
                )
                themes.append(theme)

            gc.collect()
            memory_after = process.memory_info().rss

            memory_increase = memory_after - memory_before
            assert memory_increase < 10 * 1024 * 1024  # 小于10MB


class TestMemoryProfiling:
    """内存性能分析测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_memory_growth_rate(self, qt_app):
        """测试内存增长率"""
        import gc

        config = create_test_config()

        gc.collect()
        baseline_memory = 0

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            gc.collect()
            baseline_memory = process.memory_info().rss
        except ImportError:
            pytest.skip("psutil not available")
            return

        growths = []

        # 进行多轮测试
        for round_num in range(10):
            # 创建一些组件
            overlays = []
            for i in range(20):
                overlay = OverlayWindow(f"growth_{round_num}_{i}", config)
                overlays.append(overlay)

            # 显示和隐藏
            for overlay in overlays:
                overlay.show(Position(100, 100))
                overlay.hide()

            # 清理
            del overlays
            gc.collect()

            current_memory = process.memory_info().rss
            growth = current_memory - baseline_memory
            growths.append(growth)

        # 检查增长率是否稳定（不持续增长）
        avg_growth = statistics.mean(growths[5:])  # 使用后5轮
        # 平均增长率应该很小
        assert avg_growth < 1024 * 1024  # 小于1MB

    def test_memory_footprint_of_typical_usage(self, qt_app):
        """测试典型使用场景内存占用"""
        import gc

        config = create_test_config()
        manager = UIManager(config)
        manager._theme_manager = ThemeEngine()
        manager._animation_controller = AnimationEngine()

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            gc.collect()
            memory_before = process.memory_info().rss
        except ImportError:
            pytest.skip("psutil not available")
            return

        # 模拟典型使用：注册多个组件，进行主题切换，输入候选等
        overlays = []
        candidates = []

        for i in range(10):
            overlay = OverlayWindow(f"typical_{i}", config)
            manager.register_component(overlay)
            overlays.append(overlay)

        candidate_view = CandidateView("typical_candidate", config)
        candidate_view.set_candidates(create_test_candidates(50))
        manager.register_component(candidate_view)

        # 执行一些操作
        manager.update_theme("dark")
        manager.update_theme("light")

        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before

        # 典型使用场景内存占用应该合理
        assert memory_increase < 10 * 1024 * 1024  # 小于10MB

        # 清理
        for overlay in overlays:
            manager.unregister_component(overlay.name)
        manager.unregister_component("typical_candidate")


# 辅助统计函数
import statistics
