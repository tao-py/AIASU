"""
基础类和接口测试
测试所有基础数据类和抽象接口
"""

import pytest
from PySide6.QtCore import QSize, QPoint, QRect, QObject
from PySide6.QtGui import QColor

from ...base import (
    UIState,
    Position,
    UITheme,
    CandidateItem,
    UIConfig,
    UIEvent,
    UIComponent,
    WindowComponent,
    AnimationController,
    ThemeManager,
    PositionManager,
    UIManagerInterface,
    MenuBarInterface,
    QObjectABCMeta,
)
from ...base import AnimationController as AbstractAnimationController


class MockUIComponent(UIComponent):
    """用于测试的模拟UI组件"""

    def __init__(self, name: str = "test_component", config=None):
        super().__init__(name, config)
        self.show_called = False
        self.hide_called = False
        self.theme_updated = False
        self.size_calculated = False

    def show(self, position=None):
        self.show_called = True
        self.set_state(UIState.VISIBLE)

    def hide(self):
        self.hide_called = True
        self.set_state(UIState.HIDDEN)

    def update_theme(self, theme):
        self.theme_updated = True
        self._current_theme = theme

    def get_preferred_size(self):
        self.size_calculated = True
        return QSize(100, 100)


class TestUIState:
    """UI状态枚举测试"""

    def test_ui_state_values(self):
        """测试状态枚举值"""
        assert UIState.HIDDEN.value == "hidden"
        assert UIState.VISIBLE.value == "visible"
        assert UIState.ANIMATING.value == "animating"
        assert UIState.LOADING.value == "loading"
        assert UIState.ERROR.value == "error"

    def test_ui_state_comparison(self):
        """测试状态比较"""
        state1 = UIState.HIDDEN
        state2 = UIState.HIDDEN
        state3 = UIState.VISIBLE

        assert state1 == state2
        assert state1 != state3


class TestPosition:
    """位置信息数据类测试"""

    def test_position_creation(self):
        """测试位置创建"""
        pos = Position(100, 200)
        assert pos.x == 100
        assert pos.y == 200

    def test_position_to_qpoint(self):
        """测试转换为QPoint"""
        pos = Position(150, 250)
        qpoint = pos.to_qpoint()
        assert qpoint.x() == 150
        assert qpoint.y() == 250

    def test_position_from_qpoint(self):
        """测试从QPoint创建"""
        qpoint = QPoint(300, 400)
        pos = Position.from_qpoint(qpoint)
        assert pos.x == 300
        assert pos.y == 400

    def test_position_equality(self):
        """测试位置相等性"""
        pos1 = Position(100, 200)
        pos2 = Position(100, 200)
        pos3 = Position(200, 300)

        assert pos1 == pos2
        assert pos1 != pos3


class TestUITheme:
    """主题配置数据类测试"""

    def test_theme_creation(self):
        """测试主题创建"""
        theme = UITheme(
            name="test_theme",
            background_color="#FFFFFF",
            text_color="#000000",
            accent_color="#007AFF",
            border_color="#CCCCCC",
            opacity=0.9,
            border_radius=8,
            font_family="Arial",
            font_size=14,
        )

        assert theme.name == "test_theme"
        assert theme.background_color == "#FFFFFF"
        assert theme.text_color == "#000000"
        assert theme.accent_color == "#007AFF"
        assert theme.opacity == 0.9
        assert theme.border_radius == 8
        assert theme.font_family == "Arial"
        assert theme.font_size == 14

    def test_theme_to_qcolor(self):
        """测试转换为QColor"""
        theme = UITheme(
            name="color_test",
            background_color="#FF0000",
            text_color="#00FF00",
            accent_color="#0000FF",
            border_color="#FFFF00",
            opacity=1.0,
            border_radius=0,
            font_family="Test",
            font_size=12,
        )

        bg_color = theme.to_qcolor("background_color")
        assert isinstance(bg_color, QColor)
        assert bg_color.name() == "#ff0000"

        text_color = theme.to_qcolor("text_color")
        assert isinstance(text_color, QColor)
        assert text_color.name() == "#00ff00"

    def test_theme_invalid_color_attribute(self):
        """测试无效颜色属性"""
        theme = UITheme(
            name="invalid_test",
            background_color="#000000",
            text_color="#FFFFFF",
            accent_color="#007AFF",
            border_color="#CCCCCC",
            opacity=1.0,
            border_radius=0,
            font_family="Test",
            font_size=12,
        )

        # 应该返回默认黑色
        color = theme.to_qcolor("nonexistent_attribute")
        assert isinstance(color, QColor)


class TestCandidateItem:
    """候选项目数据类测试"""

    def test_candidate_creation(self):
        """测试候选项创建"""
        candidate = CandidateItem(
            text="测试候选",
            description="测试描述",
            score=0.8,
        )

        assert candidate.text == "测试候选"
        assert candidate.description == "测试描述"
        assert candidate.score == 0.8
        assert candidate.icon is None
        assert candidate.metadata == {}

    def test_candidate_with_metadata(self):
        """测试带元数据的候选项"""
        metadata = {"key": "value", "count": 42}
        candidate = CandidateItem(
            text="带元数据的候选",
            metadata=metadata,
        )

        assert candidate.metadata == metadata

    def test_candidate_post_init(self):
        """测试__post_init__ - 自动初始化metadata"""
        candidate = CandidateItem(text="测试")
        assert candidate.metadata is not None
        assert isinstance(candidate.metadata, dict)
        assert candidate.metadata == {}

    def test_candidate_with_none_metadata(self):
        """测试显式传递None的metadata"""
        candidate = CandidateItem(text="测试", metadata=None)
        assert candidate.metadata is not None
        assert candidate.metadata == {}


class TestUIConfig:
    """UI配置数据类测试"""

    def test_config_default_values(self):
        """测试默认配置值"""
        config = UIConfig()

        assert config.theme == "default"
        assert config.opacity == 0.95
        assert config.animation_duration == 200
        assert config.max_candidates == 5
        assert config.window_padding == 8
        assert config.font_size == 14
        assert config.follow_cursor is True
        assert config.multi_monitor is True
        assert config.auto_hide_delay == 3000
        assert config.enable_animation is True

    def test_config_custom_values(self):
        """测试自定义配置值"""
        config = UIConfig(
            theme="dark",
            opacity=0.8,
            animation_duration=300,
            max_candidates=10,
            window_padding=12,
            font_size=16,
            follow_cursor=False,
            multi_monitor=False,
            auto_hide_delay=5000,
            enable_animation=False,
        )

        assert config.theme == "dark"
        assert config.opacity == 0.8
        assert config.animation_duration == 300
        assert config.max_candidates == 10
        assert config.window_padding == 12
        assert config.font_size == 16
        assert config.follow_cursor is False
        assert config.multi_monitor is False
        assert config.auto_hide_delay == 5000
        assert config.enable_animation is False


class TestUIEvent:
    """UI事件类测试"""

    def test_event_creation(self):
        """测试事件创建"""
        event = UIEvent("test_event", {"key": "value"})

        assert event.event_type == "test_event"
        assert event.data == {"key": "value"}
        assert event.timestamp == 0.0  # 默认值

    def test_event_with_none_data(self):
        """测试无数据的事件"""
        event = UIEvent("empty_event")

        assert event.event_type == "empty_event"
        assert event.data == {}

    def test_event_with_empty_dict(self):
        """测试空字典数据"""
        event = UIEvent("empty_data_event", {})

        assert event.data == {}

    def test_event_timestamp_modification(self):
        """测试时间戳修改"""
        event = UIEvent("timestamp_test")
        event.timestamp = 123456.789

        assert event.timestamp == 123456.789


class TestUIComponent:
    """UI组件抽象基类测试"""

    def test_component_initialization(self):
        """测试组件初始化"""
        config = UIConfig(theme="test")
        component = MockUIComponent("test_comp", config)

        assert component.name == "test_comp"
        assert component.config == config
        assert component.state == UIState.HIDDEN
        assert component._event_handlers == {}

    def test_component_state_transitions(self):
        """测试组件状态转换"""
        component = MockUIComponent()

        # 初始状态
        assert component.state == UIState.HIDDEN

        # 显示
        component.show()
        assert component.state == UIState.VISIBLE
        assert component.show_called is True

        # 隐藏
        component.hide()
        assert component.state == UIState.HIDDEN
        assert component.hide_called is True

    def test_component_event_handlers(self):
        """测试事件处理器"""
        component = MockUIComponent()
        handler_called = []

        def test_handler(event):
            handler_called.append(event.event_type)

        # 添加事件处理器
        component.add_event_handler("test_event", test_handler)
        assert "test_event" in component._event_handlers
        assert test_handler in component._event_handlers["test_event"]

        # 触发事件
        component._emit_event("test_event")
        assert len(handler_called) == 1
        assert handler_called[0] == "test_event"

    def test_component_remove_event_handler(self):
        """测试移除事件处理器"""
        component = MockUIComponent()
        handler_called = []

        def test_handler(event):
            handler_called.append(event.event_type)

        component.add_event_handler("test_event", test_handler)
        component.remove_event_handler("test_event", test_handler)

        # 触发事件，处理器不应被调用
        component._emit_event("test_event")
        assert len(handler_called) == 0

    def test_component_multiple_event_handlers(self):
        """测试多个事件处理器"""
        component = MockUIComponent()
        calls = []

        def handler1(event):
            calls.append(("handler1", event.event_type))

        def handler2(event):
            calls.append(("handler2", event.event_type))

        component.add_event_handler("event1", handler1)
        component.add_event_handler("event1", handler2)

        component._emit_event("event1")

        assert len(calls) == 2
        assert ("handler1", "event1") in calls
        assert ("handler2", "event1") in calls

    def test_component_abstract_methods(self):
        """测试抽象方法强制实现"""
        # 直接实例化UIComponent应该失败
        with pytest.raises(TypeError):
            UIComponent("test")

    def test_component_theme_update(self):
        """测试主题更新"""
        component = MockUIComponent()
        theme = UITheme(
            name="test",
            background_color="#000000",
            text_color="#FFFFFF",
            accent_color="#007AFF",
            border_color="#CCCCCC",
            opacity=1.0,
            border_radius=0,
            font_family="Test",
            font_size=12,
        )

        component.update_theme(theme)
        assert component.theme_updated is True
        assert component._current_theme == theme


class TestWindowComponent:
    """窗口组件抽象类测试"""

    def test_window_component_initialization(self):
        """测试窗口组件初始化"""
        config = UIConfig()
        # WindowComponent是抽象类，不能直接实例化
        with pytest.raises(TypeError):
            WindowComponent("test_window", config)

    def test_window_component_abstract_methods(self):
        """测试窗口组件抽象方法"""
        with pytest.raises(TypeError):
            WindowComponent("test")

    def test_window_component_move_to_cursor(self):
        """测试移动到光标"""
        config = UIConfig(follow_cursor=True)

        class TestWindow(WindowComponent):
            def create_window(self):
                pass

            def set_position(self, position):
                self._position = position

            def set_content(self, content):
                pass

            def show(self, position=None):
                pass

            def hide(self):
                pass

            def update_theme(self, theme):
                pass

            def get_preferred_size(self):
                from PySide6.QtCore import QSize
                return QSize(100, 100)

        window = TestWindow("test", config)
        cursor_pos = Position(500, 600)

        window.move_to_cursor(cursor_pos)
        assert window._position == cursor_pos

    def test_window_component_no_follow_cursor(self):
        """测试不跟随光标"""
        config = UIConfig(follow_cursor=False)

        class TestWindow(WindowComponent):
            def create_window(self):
                pass

            def set_position(self, position):
                self._position = position

            def set_content(self, content):
                pass

            def show(self, position=None):
                pass

            def hide(self):
                pass

            def update_theme(self, theme):
                pass

            def get_preferred_size(self):
                from PySide6.QtCore import QSize
                return QSize(100, 100)

        window = TestWindow("test", config)
        cursor_pos = Position(500, 600)
        window._position = Position(100, 100)

        window.move_to_cursor(cursor_pos)
        # 不应该改变位置
        assert window._position == Position(100, 100)


class TestAbstractInterfaces:
    """抽象接口测试"""

    def test_animation_controller_is_abstract(self):
        """测试AnimationController是抽象的"""
        with pytest.raises(TypeError):
            AnimationController()

    def test_theme_manager_is_abstract(self):
        """测试ThemeManager是抽象的"""
        with pytest.raises(TypeError):
            ThemeManager()

    def test_position_manager_is_abstract(self):
        """测试PositionManager是抽象的"""
        with pytest.raises(TypeError):
            PositionManager()

    def test_ui_manager_interface_is_abstract(self):
        """测试UIManagerInterface是抽象的"""
        with pytest.raises(TypeError):
            UIManagerInterface()

    def test_menu_bar_interface_is_abstract(self):
        """测试MenuBarInterface是抽象的"""
        with pytest.raises(TypeError):
            MenuBarInterface()


class TestQObjectABCMeta:
    """QObjectABCMeta元类测试"""

    def test_metaclass_allows_multiple_inheritance(self):
        """测试元类允许多重继承"""
        # 这个测试确保QObjectABCMeta可以正确工作
        # 我们已经在实际代码中使用它，这里只是验证没有错误

        class TestClass(QObject, UIComponent, metaclass=QObjectABCMeta):
            def __init__(self, name="test", config=None, parent=None):
                # 必须先调用QObject.__init__，传入parent
                QObject.__init__(self, parent)
                # 然后调用UIComponent.__init__
                UIComponent.__init__(self, name, config)

            def show(self, position=None):
                pass

            def hide(self):
                pass

            def update_theme(self, theme):
                pass

            def get_preferred_size(self):
                return QSize(100, 100)

        # 应该能成功创建实例
        instance = TestClass("test")
        # 验证实例创建成功且具有QObject特性
        assert isinstance(instance, QObject)
        assert isinstance(instance, UIComponent)
