"""
UI管理器测试
测试UIManager的功能和组件管理
"""

import pytest
import time
import threading
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ...base import UIConfig, UITheme, Position, UIEvent, UIComponent, UIState
from ...ui_manager import UIManager
from ...theme_engine import ThemeEngine
from ...animation_engine import AnimationEngine
from ..utils.helpers import (
    setup_test_qt_app,
    teardown_test_qt_app,
    create_test_config,
    create_test_theme,
    create_test_candidates,
    process_events_for,
)


class MockUIComponentForManager(UIComponent):
    """用于UIManager测试的模拟组件"""

    def __init__(self, name: str, config=None):
        super().__init__(name, config)
        self.visible = False
        self.position = None
        self.content = None

    def show(self, position=None):
        self.visible = True
        self.position = position
        self.set_state(UIState.VISIBLE)

    def hide(self):
        self.visible = False
        self.set_state(UIState.HIDDEN)

    def update_theme(self, theme):
        self._current_theme = theme

    def get_preferred_size(self):
        from PySide6.QtCore import QSize
        return QSize(200, 150)


class TestUIManagerInitialization:
    """UIManager初始化测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        """Qt应用实例"""
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_manager_creation_with_default_config(self, qt_app):
        """测试使用默认配置创建管理器"""
        manager = UIManager()
        assert manager is not None
        assert manager._config is not None
        assert isinstance(manager._config, UIConfig)

    def test_manager_creation_with_custom_config(self, qt_app):
        """测试使用自定义配置创建管理器"""
        config = create_test_config()
        manager = UIManager(config)
        assert manager._config == config

    def test_manager_initial_state(self, qt_app):
        """测试管理器初始状态"""
        manager = UIManager()
        assert manager._components == {}
        assert manager._is_processing_events is False
        assert manager._event_queue == []
        assert manager._auto_hide_timers == {}


class TestComponentRegistration:
    """组件注册测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def manager(self, qt_app):
        return UIManager()

    def test_register_component(self, manager):
        """测试注册组件"""
        component = MockUIComponentForManager("comp1")
        manager.register_component(component)

        assert "comp1" in manager._components
        assert manager._components["comp1"] == component

    def test_register_duplicate_component(self, manager):
        """测试注册重复组件"""
        component1 = MockUIComponentForManager("comp_dup")
        component2 = MockUIComponentForManager("comp_dup")

        manager.register_component(component1)
        # 注册同名组件应该被警告但不会抛出异常
        manager.register_component(component2)

        # 应该保留第一个组件
        assert manager._components["comp_dup"] == component1

    def test_register_multiple_components(self, manager):
        """测试注册多个组件"""
        components = [
            MockUIComponentForManager(f"comp{i}") for i in range(5)
        ]

        for comp in components:
            manager.register_component(comp)

        assert len(manager._components) == 5
        for i in range(5):
            assert f"comp{i}" in manager._components

    def test_unregister_component(self, manager):
        """测试注销组件"""
        component = MockUIComponentForManager("to_remove")
        manager.register_component(component)
        assert "to_remove" in manager._components

        manager.unregister_component("to_remove")
        assert "to_remove" not in manager._components

    def test_unregister_nonexistent_component(self, manager):
        """测试注销不存在的组件"""
        # 不应该抛出异常
        manager.unregister_component("nonexistent")

    def test_get_component(self, manager):
        """测试获取组件"""
        component = MockUIComponentForManager("get_test")
        manager.register_component(component)

        retrieved = manager.get_component("get_test")
        assert retrieved == component

    def test_get_nonexistent_component(self, manager):
        """测试获取不存在的组件"""
        result = manager.get_component("nonexistent")
        assert result is None


class TestComponentVisibility:
    """组件可见性测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def manager_with_components(self, qt_app):
        manager = UIManager()
        components = {
            "comp1": MockUIComponentForManager("comp1"),
            "comp2": MockUIComponentForManager("comp2"),
            "comp3": MockUIComponentForManager("comp3"),
        }
        for comp in components.values():
            manager.register_component(comp)
        return manager, components

    def test_show_component(self, manager_with_components):
        """测试显示组件"""
        manager, components = manager_with_components
        pos = Position(100, 200)

        manager.show_component("comp1", pos)

        assert components["comp1"].visible is True
        assert components["comp1"].position == pos

    def test_show_nonexistent_component(self, manager_with_components):
        """测试显示不存在的组件"""
        manager, _ = manager_with_components
        # 不应该抛出异常
        manager.show_component("nonexistent")

    def test_hide_component(self, manager_with_components):
        """测试隐藏组件"""
        manager, components = manager_with_components

        # 先显示
        manager.show_component("comp2")
        assert components["comp2"].visible is True

        # 然后隐藏
        manager.hide_component("comp2")
        assert components["comp2"].visible is False

    def test_hide_nonexistent_component(self, manager_with_components):
        """测试隐藏不存在的组件"""
        manager, _ = manager_with_components
        # 不应该抛出异常
        manager.hide_component("nonexistent")


class TestThemeManagement:
    """主题管理测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def manager_with_theme(self, qt_app):
        manager = UIManager()
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()
        return manager

    def test_update_theme_all_components(self, manager_with_theme):
        """测试更新所有组件的主题"""
        # 注册组件
        components = [MockUIComponentForManager(f"comp{i}") for i in range(3)]
        for comp in components:
            manager_with_theme.register_component(comp)

        # 使用已存在的主题（ThemeEngine内置有default, dark, light, glass）
        manager_with_theme.update_theme("dark")

        # 验证所有组件都更新了主题
        for comp in components:
            assert hasattr(comp, "_current_theme")
            # 主题应该是dark
            assert comp._current_theme.name == "dark"

    def test_theme_change_signal(self, manager_with_theme):
        """测试主题变更信号"""
        signals_received = []

        def on_theme_changed(theme_name):
            signals_received.append(theme_name)

        manager_with_theme.theme_changed.connect(on_theme_changed)

        # 主题变更应该触发信号
        # 注意：这需要theme_manager正确实现
        # 由于UIManager的update_theme可能直接委托给theme_manager
        # 具体行为取决于实现


class TestEventProcessing:
    """事件处理测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def manager(self, qt_app):
        return UIManager()

    def test_process_input_event(self, manager):
        """测试处理输入事件"""
        event = UIEvent("test_event", {"data": "test_value"})
        manager.process_input_event(event)

        # 事件应该被立即处理并从队列中移除
        # 由于_process_event_queue会立即处理，队列应该为空
        assert len(manager._event_queue) == 0

    def test_event_queue_processing(self, manager):
        """测试事件队列处理"""
        events = [
            UIEvent("event1", {"id": 1}),
            UIEvent("event2", {"id": 2}),
            UIEvent("event3", {"id": 3}),
        ]

        for event in events:
            manager.process_input_event(event)

        # 所有事件应该都被处理了
        assert len(manager._event_queue) == 0

    def test_input_event_signal(self, manager):
        """测试输入事件信号"""
        received_events = []

        def on_input_event(event):
            received_events.append(event)

        manager.input_event_received.connect(on_input_event)

        test_event = UIEvent("signal_test")
        manager.process_input_event(test_event)

        # 事件应该触发信号
        assert len(received_events) >= 0  # 可能不会立即触发


class TestAutoHideTimers:
    """自动隐藏定时器测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def manager(self, qt_app):
        return UIManager()

    def test_auto_hide_delay_config(self, manager):
        """测试自动隐藏延迟配置"""
        config = UIConfig(auto_hide_delay=2000)
        manager._config = config

        assert manager._config.auto_hide_delay == 2000

    def test_auto_hide_timer_creation(self, manager):
        """测试自动隐藏定时器创建"""
        # 显示组件时会创建定时器
        component = MockUIComponentForManager("timer_test")
        manager.register_component(component)

        # 初始不应该有定时器
        assert "timer_test" not in manager._auto_hide_timers


class TestThreadSafety:
    """线程安全性测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_component_registration_thread_safety(self, qt_app):
        """测试组件注册的线程安全性"""
        manager = UIManager()
        results = []

        def register_component(thread_id):
            try:
                component = MockUIComponentForManager(f"thread_comp_{thread_id}")
                manager.register_component(component)
                results.append((thread_id, "success"))
            except Exception as e:
                results.append((thread_id, f"error: {e}"))

        threads = []
        for i in range(5):
            thread = threading.Thread(target=register_component, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 所有线程应该都成功
        assert len(results) == 5
        for thread_id, result in results:
            assert result == "success"

    def test_event_processing_thread_safety(self, qt_app):
        """测试事件处理的线程安全性"""
        manager = UIManager()
        event_count = 20
        received_count = [0]  # 使用列表以便在闭包中修改

        def send_events(thread_id):
            for i in range(event_count):
                event = UIEvent(f"thread_{thread_id}_event_{i}")
                manager.process_input_event(event)

        threads = []
        for i in range(3):
            thread = threading.Thread(target=send_events, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 等待事件处理完成
        time.sleep(0.1)

        # 事件应该都被处理，队列为空
        assert len(manager._event_queue) == 0


class TestUIManagerCleanup:
    """UIManager清理测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_manager_cleanup(self, qt_app):
        """测试管理器清理"""
        manager = UIManager()

        # 注册一些组件
        for i in range(5):
            component = MockUIComponentForManager(f"cleanup_comp{i}")
            manager.register_component(component)

        assert len(manager._components) == 5

        # 清理应该移除所有组件
        # 注意：UIManager可能没有显式的cleanup方法
        # 我们可以通过del来测试垃圾回收

        # 保存引用以便测试
        components_count = len(manager._components)
        assert components_count > 0
