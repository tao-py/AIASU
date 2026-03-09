"""
性能基准测试
测试UI组件的性能指标
"""

import pytest
import time
import statistics
from PySide6.QtWidgets import QApplication

from ...base import Position, CandidateItem
from ...ui_manager import UIManager
from ...animation_engine import AnimationEngine
from ...theme_engine import ThemeEngine
from ...overlay_window import OverlayWindow
from ...candidate_view import CandidateView
from ...ime_window import IMEWindow
from ...input_preview import InputPreview
from ..utils.helpers import (
    setup_test_qt_app,
    teardown_test_qt_app,
    create_test_config,
    create_test_candidates,
    process_events_for,
)


class TestPerformanceBaseline:
    """性能基线测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_component_creation_performance(self, qt_app):
        """测试组件创建性能"""
        config = create_test_config()
        times = []

        for _ in range(100):
            start = time.perf_counter()
            overlay = OverlayWindow("perf_overlay", config)
            end = time.perf_counter()
            times.append(end - start)
            overlay.hide()

        avg_time = statistics.mean(times)
        max_time = max(times)

        assert avg_time < 0.01  # 平均小于10ms
        assert max_time < 0.05  # 最大小于50ms

    def test_manager_registration_performance(self, qt_app):
        """测试管理器注册性能"""
        config = create_test_config()
        manager = UIManager(config)
        times = []

        for i in range(100):
            start = time.perf_counter()
            comp = OverlayWindow(f"reg_perf_{i}", config)
            manager.register_component(comp)
            end = time.perf_counter()
            times.append(end - start)
            manager.unregister_component(comp.name)

        avg_time = statistics.mean(times)
        assert avg_time < 0.005  # 平均小于5ms

    def test_theme_application_performance(self, qt_app):
        """测试主题应用性能"""
        config = create_test_config()
        manager = UIManager(config)
        manager._theme_manager = ThemeEngine()

        # 注册多个组件
        for i in range(20):
            comp = OverlayWindow(f"theme_perf_{i}", config)
            manager.register_component(comp)

        times = []
        for _ in range(50):
            start = time.perf_counter()
            manager.update_theme("dark")
            end = time.perf_counter()
            times.append(end - start)

        avg_time = statistics.mean(times)
        assert avg_time < 0.01  # 平均小于10ms


class TestAnimationPerformance:
    """动画性能测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_fade_animation_startup_time(self, qt_app):
        """测试淡入动画启动时间"""
        config = create_test_config()
        engine = AnimationEngine(config)
        overlay = OverlayWindow("fade_perf", config)

        times = []
        for _ in range(50):
            start = time.perf_counter()
            engine.fade_in(overlay, duration=100)
            end = time.perf_counter()
            times.append(end - start)
            engine.clear_animations()

        avg_time = statistics.mean(times)
        assert avg_time < 0.01  # 动画启动应快速

    def test_multiple_animation_overhead(self, qt_app):
        """测试多个动画开销"""
        config = create_test_config()
        engine = AnimationEngine(config)

        overlays = [OverlayWindow(f"multi_anim_{i}", config) for i in range(10)]

        start = time.perf_counter()
        for overlay in overlays:
            engine.fade_in(overlay, duration=50)
        end = time.perf_counter()

        total_time = end - start
        assert total_time < 0.1  # 10个动画启动应快速

        engine.clear_animations()

    def test_animation_cleanup_performance(self, qt_app):
        """测试动画清理性能"""
        config = create_test_config()
        engine = AnimationEngine(config)

        # 添加大量动画
        for i in range(100):
            overlay = OverlayWindow(f"cleanup_{i}", config)
            engine.fade_in(overlay, duration=100)

        start = time.perf_counter()
        engine.clear_animations()
        end = time.perf_counter()

        cleanup_time = end - start
        assert cleanup_time < 0.05  # 清理应该快速
        assert len(engine._active_animations) == 0


class TestMemoryPerformance:
    """内存性能测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_component_creation_memory_usage(self, qt_app):
        """测试组件创建内存使用"""
        import gc

        config = create_test_config()

        # 测量创建前内存
        gc.collect()

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss
        except ImportError:
            pytest.skip("psutil not available")
            return

        # 创建多个组件
        overlays = []
        for i in range(50):
            overlay = OverlayWindow(f"mem_test_{i}", config)
            overlays.append(overlay)

        gc.collect()
        memory_after = process.memory_info().rss

        # 清理
        for overlay in overlays:
            overlay.hide()
        overlays.clear()
        gc.collect()

        memory_final = process.memory_info().rss

        # 创建50个组件增加的内存应该合理
        memory_increase = memory_after - memory_before
        assert memory_increase < 10 * 1024 * 1024  # 小于10MB

        # 清理后应该回收大部分内存
        memory_after_cleanup = memory_final - memory_before
        assert memory_after_cleanup < memory_increase * 0.5  # 至少回收一半

    def test_no_memory_leak_in_repeated_operations(self, qt_app):
        """测试重复操作无内存泄漏"""
        import gc

        config = create_test_config()
        manager = UIManager(config)
        manager._theme_manager = ThemeEngine()

        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
        except ImportError:
            pytest.skip("psutil not available")
            return

        initial_memory = process.memory_info().rss

        # 执行大量重复操作
        for _ in range(100):
            overlay = OverlayWindow("leak_test", config)
            manager.register_component(overlay)
            manager.show_component("leak_test")
            manager.hide_component("leak_test")
            manager.unregister_component("leak_test")

        gc.collect()
        final_memory = process.memory_info().rss

        memory_increase = final_memory - initial_memory
        # 内存增长应该很小（小于1MB）
        assert memory_increase < 1024 * 1024

    def test_candidate_list_memory_efficiency(self, qt_app):
        """测试候选列表内存效率"""
        import gc

        config = create_test_config()
        candidate_view = CandidateView("mem_candidate", config)

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
        large_candidates = create_test_candidates(1000)
        candidate_view.set_candidates(large_candidates)

        gc.collect()
        memory_after = process.memory_info().rss

        memory_increase = memory_after - memory_before
        # 1000个候选项增加的内存应该合理
        assert memory_increase < 5 * 1024 * 1024  # 小于5MB


class TestRenderingPerformance:
    """渲染性能测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_component_show_hide_performance(self, qt_app):
        """测试组件显示隐藏性能"""
        config = create_test_config()
        overlay = OverlayWindow("show_hide_perf", config)

        times = []
        for _ in range(50):
            start = time.perf_counter()
            overlay.show(Position(100, 100))
            overlay.hide()
            end = time.perf_counter()
            times.append(end - start)

        avg_time = statistics.mean(times)
        assert avg_time < 0.02  # 每次显示隐藏平均小于20ms

    def test_multiple_component_show_hide_performance(self, qt_app):
        """测试多个组件显示隐藏性能"""
        config = create_test_config()
        overlays = [OverlayWindow(f"multi_{i}", config) for i in range(10)]

        start = time.perf_counter()
        for _ in range(10):
            for overlay in overlays:
                overlay.show(Position(100, 100))
                overlay.hide()
        end = time.perf_counter()

        total_time = end - start
        operations = 10 * 10 * 2  # 10轮 * 10组件 * 2操作
        avg_time_per_op = total_time / operations

        assert avg_time_per_op < 0.01  # 每次操作平均小于10ms


class TestConcurrencyPerformance:
    """并发性能测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_concurrent_component_operations(self, qt_app):
        """测试并发组件操作性能"""
        import threading
        import queue

        config = create_test_config()
        manager = UIManager(config)
        manager._theme_manager = ThemeEngine()

        results = queue.Queue()

        def worker(thread_id):
            try:
                comp_name = f"concurrent_{thread_id}"
                comp = OverlayWindow(comp_name, config)
                manager.register_component(comp)
                manager.show_component(comp_name)
                manager.hide_component(comp_name)
                manager.unregister_component(comp_name)
                results.put(True)
            except Exception as e:
                results.put(f"Error: {e}")

        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 检查所有线程成功
        successes = 0
        while not results.empty():
            if results.get() is True:
                successes += 1

        assert successes == 10

    def test_concurrent_theme_updates(self, qt_app):
        """测试并发主题更新性能"""
        import threading
        import queue

        config = create_test_config()
        manager = UIManager(config)
        manager._theme_manager = ThemeEngine()

        # 注册一些组件
        for i in range(10):
            comp = OverlayWindow(f"concurrent_theme_{i}", config)
            manager.register_component(comp)

        results = queue.Queue()
        themes = ["default", "dark", "light", "glass"]

        def theme_updater(thread_id):
            try:
                for theme in themes:
                    manager.update_theme(theme)
                results.put(True)
            except Exception as e:
                results.put(f"Error: {e}")

        threads = []
        for i in range(5):
            thread = threading.Thread(target=theme_updater, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        successes = 0
        while not results.empty():
            if results.get() is True:
                successes += 1

        assert successes == 5


class TestScalability:
    """可扩展性测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_many_components_performance(self, qt_app):
        """测试大量组件的性能"""
        import time

        config = create_test_config()
        manager = UIManager(config)

        start = time.perf_counter()

        # 创建100个组件
        for i in range(100):
            comp = OverlayWindow(f"many_{i}", config)
            manager.register_component(comp)

        registration_time = time.perf_counter() - start

        assert registration_time < 1.0  # 100个组件注册应小于1秒
        assert len(manager._components) == 100

        # 测试主题更新性能
        start = time.perf_counter()
        manager.update_theme("dark")
        theme_time = time.perf_counter() - start

        assert theme_time < 0.5  # 100个组件主题更新应小于0.5秒

        # 清理
        for i in range(100):
            manager.unregister_component(f"many_{i}")

    def test_large_candidate_list_performance(self, qt_app):
        """测试大候选列表性能"""
        config = create_test_config()
        candidate_view = CandidateView("large_perf", config)

        # 创建1000个候选项
        large_candidates = create_test_candidates(1000)

        start = time.perf_counter()
        candidate_view.set_candidates(large_candidates)
        set_time = time.perf_counter() - start

        assert set_time < 0.5  # 设置1000个候选应小于0.5秒
        assert len(candidate_view._candidates) == 1000

    def test_deep_theme_hierarchy_performance(self, qt_app):
        """测试深主题层次性能（如果有继承）"""
        from ...theme_engine import ThemeEngine
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            engine = ThemeEngine(temp_dir)

            # 创建多层级的自定义主题
            start = time.perf_counter()

            for i in range(10):
                engine.create_custom_theme(
                    f"hierarchy_theme_{i}",
                    "default",
                    background_color=f"#{i:02x}{i:02x}{i:02x}",
                )

            creation_time = time.perf_counter() - start

            assert creation_time < 1.0  # 创建10个主题应小于1秒


class TestStartupPerformance:
    """启动性能测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_manager_startup_time(self, qt_app):
        """测试管理器启动时间"""
        start = time.perf_counter()
        manager = UIManager()
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()
        end = time.perf_counter()

        startup_time = end - start
        assert startup_time < 0.1  # 启动应小于100ms

    def test_engine_startup_time(self, qt_app):
        """测试引擎启动时间"""
        start = time.perf_counter()
        engine = AnimationEngine()
        end = time.perf_counter()

        startup_time = end - start
        assert startup_time < 0.05  # 启动应小于50ms

    def test_theme_engine_startup_time(self, qt_app):
        """测试主题引擎启动时间"""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            start = time.perf_counter()
            engine = ThemeEngine(temp_dir)
            end = time.perf_counter()

            startup_time = end - start
            assert startup_time < 0.2  # 启动应小于200ms


class TestIOPerformance:
    """I/O性能测试"""

    def test_config_io_performance(self):
        """测试配置I/O性能"""
        from ...config_manager import ConfigManager
        import tempfile
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)

            # 写入性能
            start = time.perf_counter()
            for i in range(100):
                manager.set(f"key_{i}", f"value_{i}")
            manager.save_config()
            write_time = time.perf_counter() - start

            assert write_time < 0.5  # 写入100个配置应小于0.5秒

            # 读取性能
            new_manager = ConfigManager(temp_dir)
            start = time.perf_counter()
            for i in range(100):
                value = new_manager.get(f"key_{i}")
                assert value == f"value_{i}"
            read_time = time.perf_counter() - start

            assert read_time < 0.5  # 读取100个配置应小于0.5秒

    def test_theme_io_performance(self):
        """测试主题I/O性能"""
        from ...theme_engine import ThemeEngine
        import tempfile
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            engine = ThemeEngine(temp_dir)

            # 保存多个主题
            start = time.perf_counter()
            for i in range(20):
                theme = engine.create_custom_theme(
                    f"io_theme_{i}",
                    "default",
                    background_color=f"#{(i * 10) % 256:02x}{(i * 20) % 256:02x}{(i * 30) % 256:02x}",
                )
                engine.save_theme(theme)
            save_time = time.perf_counter() - start

            assert save_time < 1.0  # 保存20个主题应小于1秒
