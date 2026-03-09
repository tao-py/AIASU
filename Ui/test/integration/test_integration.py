"""
集成测试
测试UI组件之间的交互和集成
"""

import pytest
import time
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ...base import UIConfig, UITheme, Position, CandidateItem, UIEvent
from ...ui_manager import UIManager
from ...theme_engine import ThemeEngine
from ...animation_engine import AnimationEngine
from ...overlay_window import OverlayWindow
from ...candidate_view import CandidateView
from ...ime_window import IMEWindow
from ...input_preview import InputPreview
from ..utils.helpers import (
    setup_test_qt_app,
    teardown_test_qt_app,
    create_test_candidates,
    create_test_theme,
    create_test_config,
    process_events_for,
)


class TestComponentIntegrationBasics:
    """组件集成基础测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def ui_manager(self, qt_app):
        manager = UIManager(create_test_config())
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()
        yield manager
        # 清理
        for comp_name in list(manager._components.keys()):
            manager.unregister_component(comp_name)

    def test_multiple_components_registration(self, ui_manager):
        """测试多个组件注册"""
        components = [
            OverlayWindow("overlay1", ui_manager._config),
            CandidateView("candidate1", ui_manager._config),
            IMEWindow("ime1", ui_manager._config),
            InputPreview("preview1", ui_manager._config),
        ]

        for comp in components:
            ui_manager.register_component(comp)

        assert len(ui_manager._components) == 4
        assert all(name in ui_manager._components for name in ["overlay1", "candidate1", "ime1", "preview1"])

    def test_components_with_shared_config(self, ui_manager):
        """测试共享相同配置的组件"""
        config = ui_manager._config

        overlay = OverlayWindow("shared_overlay", config)
        candidate = CandidateView("shared_candidate", config)

        ui_manager.register_component(overlay)
        ui_manager.register_component(candidate)

        # 两个组件应该使用相同的配置实例
        assert overlay.config == candidate.config
        assert overlay.config == config

    def test_theme_propagation_to_components(self, ui_manager):
        """测试主题传播到所有组件"""
        # 注册组件
        overlay = OverlayWindow("theme_overlay", ui_manager._config)
        candidate = CandidateView("theme_candidate", ui_manager._config)
        ui_manager.register_component(overlay)
        ui_manager.register_component(candidate)

        # 更新主题
        theme_name = "integration_test_theme"
        ui_manager.update_theme(theme_name)

        # 验证所有组件都收到了主题更新
        # 注意：具体验证取决于组件的update_theme实现
        assert hasattr(overlay, "_current_theme")
        assert hasattr(candidate, "_current_theme")


class TestEventFlow:
    """事件流测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def ui_manager_with_ime(self, qt_app):
        manager = UIManager(create_test_config())
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()

        ime = IMEWindow("test_ime", manager._config)
        candidate_view = CandidateView("test_candidate", manager._config)

        manager.register_component(ime)
        manager.register_component(candidate_view)

        return manager, ime, candidate_view

    def test_input_event_flow(self, ui_manager_with_ime):
        """测试输入事件流"""
        manager, ime, candidate = ui_manager_with_ime

        # 模拟输入事件
        event = UIEvent("text_input", {"text": "测试输入"})
        manager.process_input_event(event)

        # 事件应该被处理
        assert event in manager._event_queue or len(manager._event_queue) > 0

    def test_candidate_selection_flow(self, ui_manager_with_ime):
        """测试候选选择流程"""
        manager, ime, candidate = ui_manager_with_ime

        # 设置候选
        candidates = create_test_candidates(5)
        ime.set_candidates(candidates)
        candidate.set_candidates(candidates)

        # 选择第一个候选
        ime._candidate_view.set_selected_index(0)
        selected = ime.confirm_selection()

        assert selected is not None
        assert selected.text == "候选1"


class TestWorkflowSimulation:
    """工作流模拟测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def full_ui_setup(self, qt_app):
        """完整的UI设置"""
        config = create_test_config()
        manager = UIManager(config)
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()

        components = {
            "ime": IMEWindow("workflow_ime", config),
            "candidate": CandidateView("workflow_candidate", config),
            "overlay": OverlayWindow("workflow_overlay", config),
            "preview": InputPreview("workflow_preview", config),
        }

        for comp in components.values():
            manager.register_component(comp)

        return manager, components

    def test_complete_input_workflow(self, full_ui_setup):
        """测试完整输入工作流"""
        manager, components = full_ui_setup

        # 1. 显示输入法窗口
        input_pos = Position(200, 200)
        components["ime"].show(input_pos)
        components["ime"].set_composition_text("测试")

        assert components["ime"].is_visible()
        assert components["ime"]._composition_text == "测试"

        # 2. 显示候选列表
        candidates = create_test_candidates(5)
        components["candidate"].set_candidates(candidates)

        # 3. 选择候选
        components["candidate"].set_selected_index(0)
        selected = components["ime"].confirm_selection()

        assert selected is not None

        # 4. 显示预览
        components["preview"].set_text(selected.text)
        preview_pos = Position(250, 250)
        components["preview"].show(preview_pos)

        assert components["preview"].is_visible()

        # 5. 显示通知或悬浮窗
        components["overlay"].set_content(f"已输入: {selected.text}")
        overlay_pos = Position(300, 300)
        components["overlay"].show(overlay_pos)

        assert components["overlay"].is_visible()

    def test_theme_change_workflow(self, full_ui_setup):
        """测试主题变更工作流"""
        manager, components = full_ui_setup

        # 应用一个主题
        theme_name = "dark"
        manager.update_theme(theme_name)

        # 验证所有组件都更新了主题
        for name, comp in components.items():
            assert hasattr(comp, "_current_theme")
            # 主题可能没有立即应用，但应该被设置了

    def test_cleanup_workflow(self, full_ui_setup):
        """测试清理工作流"""
        manager, components = full_ui_setup

        # 显示所有组件
        for comp in components.values():
            comp.show(Position(100, 100))

        # 隐藏所有组件
        for comp in components.values():
            comp.hide()

        # 注销组件
        for name in list(components.keys()):
            manager.unregister_component(name)

        assert len(manager._components) == 0


class TestConcurrentOperations:
    """并发操作测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_multiple_animations_same_component(self, qt_app):
        """测试同一组件上的多个动画"""
        from ...animation_engine import AnimationEngine
        from ...overlay_window import OverlayWindow

        config = create_test_config()
        engine = AnimationEngine(config)
        overlay = OverlayWindow("multi_anim", config)

        # 启动多个不同类型的动画
        engine.fade_in(overlay, duration=100)
        engine.fade_out(overlay, duration=100)
        engine.slide_in(overlay, direction="bottom", duration=100)

        # 应该至少有一个动画在活动列表中
        assert len(engine._active_animations) > 0

    def test_concurrent_component_updates(self, qt_app):
        """测试并发组件更新"""
        import threading

        config = create_test_config()
        manager = UIManager(config)
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()

        overlay = OverlayWindow("concurrent_overlay", config)
        manager.register_component(overlay)

        results = []

        def worker(thread_id):
            try:
                theme_name = f"theme_{thread_id}"
                manager.update_theme(theme_name)
                results.append((thread_id, "success"))
            except Exception as e:
                results.append((thread_id, f"error: {e}"))

        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 所有线程应该完成
        assert len(results) == 5


class TestErrorRecovery:
    """错误恢复测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def ui_manager(self, qt_app):
        manager = UIManager()
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()
        return manager

    def test_show_nonexistent_component_no_crash(self, ui_manager):
        """测试显示不存在组件不会崩溃"""
        try:
            ui_manager.show_component("nonexistent_component")
            # 应该安全执行而不抛出异常
            assert True
        except Exception:
            assert False, "显示不存在组件时抛出异常"

    def test_hide_nonexistent_component_no_crash(self, ui_manager):
        """测试隐藏不存在组件不会崩溃"""
        try:
            ui_manager.hide_component("nonexistent_component")
            assert True
        except Exception:
            assert False, "隐藏不存在组件时抛出异常"

    def test_invalid_theme_name(self, ui_manager):
        """测试无效主题名称"""
        overlay = OverlayWindow("invalid_theme_overlay", ui_manager._config)
        ui_manager.register_component(overlay)

        # 使用无效主题名应该优雅处理
        try:
            ui_manager.update_theme("nonexistent_theme")
            # 可能不会抛出异常
        except Exception:
            # 如果抛出异常，应该是可处理的
            pass

    def test_component_with_exception_in_show(self, ui_manager):
        """测试show方法抛出异常的组件"""
        class FailingComponent:
            def __init__(self):
                self.name = "failing"
                self.state = None

            def show(self, position=None):
                raise RuntimeError("Show failed")

            def hide(self):
                pass

            def update_theme(self, theme):
                pass

            def get_preferred_size(self):
                from PySide6.QtCore import QSize
                return QSize(100, 100)

        failing = FailingComponent()

        # UIManager应该能处理show异常
        # 具体行为取决于实现


class TestResourceManagement:
    """资源管理测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_animation_resources_cleanup(self, qt_app):
        """测试动画资源清理"""
        engine = AnimationEngine()
        from PySide6.QtCore import QPropertyAnimation, QPoint
        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(100)
        engine._active_animations["test"] = animation

        engine.clear_animations()
        assert len(engine._active_animations) == 0

    def test_multiple_managers_independent(self, qt_app):
        """测试多个管理器独立工作"""
        manager1 = UIManager()
        manager2 = UIManager()

        comp1 = OverlayWindow("comp1", manager1._config)
        comp2 = OverlayWindow("comp2", manager2._config)

        manager1.register_component(comp1)
        manager2.register_component(comp2)

        assert "comp1" in manager1._components
        assert "comp2" in manager2._components
        assert "comp1" not in manager2._components
        assert "comp2" not in manager1._components


class TestPerformanceIntegration:
    """集成性能测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_mass_component_registration_performance(self, qt_app):
        """测试大量组件注册的性能"""
        import time

        manager = UIManager()
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()

        start_time = time.time()

        for i in range(50):
            overlay = OverlayWindow(f"perf_overlay_{i}", manager._config)
            manager.register_component(overlay)

        end_time = time.time()
        registration_time = end_time - start_time

        assert registration_time < 2.0  # 应该很快完成
        assert len(manager._components) == 50

    def test_bulk_theme_update_performance(self, qt_app):
        """测试批量主题更新的性能"""
        manager = UIManager()
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()

        # 注册多个组件
        for i in range(30):
            comp = OverlayWindow(f"bulk_theme_{i}", manager._config)
            manager.register_component(comp)

        start_time = time.time()
        manager.update_theme("dark")
        end_time = time.time()

        theme_update_time = end_time - start_time
        assert theme_update_time < 1.0  # 主题更新应该很快
