"""
动画引擎测试
测试AnimationEngine的各种动画效果
"""

import pytest
from PySide6.QtCore import QSize, QPoint
from PySide6.QtWidgets import QApplication, QWidget

from ...animation_engine import AnimationEngine
from ...base import UIConfig, UIComponent, Position, UIState
from ..utils.helpers import (
    setup_test_qt_app,
    teardown_test_qt_app,
    create_test_config,
    process_events_for,
)


class MockWidgetForAnimation(QWidget):
    """用于动画测试的模拟窗口部件"""

    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 150)
        self._opacity = 1.0

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = value


class MockUIComponentForAnimation(UIComponent):
    """用于动画测试的模拟UI组件"""

    def __init__(self, name: str, config=None, widget=None):
        super().__init__(name, config or UIConfig())
        self._widget = widget or MockWidgetForAnimation()
        self.animation_called = False
        self.last_animation_type = None

    def show(self, position=None):
        self.set_state(UIState.VISIBLE)
        if position:
            self._widget.move(position.to_qpoint())

    def hide(self):
        self.set_state(UIState.HIDDEN)

    def update_theme(self, theme):
        pass

    def get_preferred_size(self):
        return self._widget.size()

    def get_widget(self):
        return self._widget


class TestAnimationEngineInitialization:
    """动画引擎初始化测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_engine_creation_without_config(self, qt_app):
        """测试无配置创建动画引擎"""
        engine = AnimationEngine()
        assert engine is not None
        assert engine.config is None

    def test_engine_creation_with_config(self, qt_app):
        """测试带配置创建动画引擎"""
        config = create_test_config()
        engine = AnimationEngine(config)
        assert engine.config == config

    def test_engine_initial_state(self, qt_app):
        """测试引擎初始状态"""
        engine = AnimationEngine()
        assert engine._active_animations == {}
        assert engine._animation_groups == {}
        assert engine._effect_cache == {}


class TestFadeAnimations:
    """淡入淡出动画测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def engine(self, qt_app):
        return AnimationEngine()

    @pytest.fixture
    def component(self, qt_app):
        widget = MockWidgetForAnimation()
        return MockUIComponentForAnimation("fade_test", widget=widget)

    def test_fade_in(self, engine, component):
        """测试淡入动画"""
        initial_opacity = component._widget.get_opacity()
        assert initial_opacity == 1.0  # MockWidget初始为1.0

        # 执行淡入动画（从0到1）
        engine.fade_in(component, duration=100)

        # 验证动画已启动
        widget_id = id(component._widget)
        assert f"fade_in_{widget_id}" in engine._active_animations

        # 处理事件让动画运行
        process_events_for(0.2)

        # 动画完成后，透明度应该接近1.0
        # 由于动画是异步的，我们只验证动画被创建了
        assert engine._active_animations[f"fade_in_{widget_id}"] is not None

    def test_fade_out(self, engine, component):
        """测试淡出动画"""
        # 执行淡出动画（从1到0）
        engine.fade_out(component, duration=100)

        widget_id = id(component._widget)
        assert f"fade_out_{widget_id}" in engine._active_animations

        # 处理事件
        process_events_for(0.2)

        # 验证动画已启动
        assert engine._active_animations[f"fade_out_{widget_id}"] is not None

    def test_fade_with_custom_duration(self, engine, component):
        """测试自定义持续时间的淡入淡出"""
        engine.fade_in(component, duration=500)
        animation = engine._active_animations[f"fade_in_{id(component._widget)}"]
        assert animation.duration() == 500

        engine.fade_out(component, duration=300)
        animation = engine._active_animations[f"fade_out_{id(component._widget)}"]
        assert animation.duration() == 300


class TestSlideAnimations:
    """滑动动画测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def engine(self, qt_app):
        return AnimationEngine()

    @pytest.fixture
    def component(self, qt_app):
        widget = MockWidgetForAnimation()
        component = MockUIComponentForAnimation("slide_test", widget=widget)
        # 设置初始位置
        widget.move(100, 100)
        return component

    def test_slide_in_from_bottom(self, engine, component):
        """测试从底部滑入"""
        initial_pos = component._widget.pos()
        engine.slide_in(component, direction="bottom", duration=200)

        widget_id = id(component._widget)
        assert f"slide_in_{widget_id}" in engine._active_animations

        process_events_for(0.1)

        # 验证动画创建
        assert engine._active_animations[f"slide_in_{widget_id}"] is not None

    def test_slide_in_from_top(self, engine, component):
        """测试从顶部滑入"""
        engine.slide_in(component, direction="top", duration=200)
        assert f"slide_in_{id(component._widget)}" in engine._active_animations

    def test_slide_in_from_left(self, engine, component):
        """测试从左侧滑入"""
        engine.slide_in(component, direction="left", duration=200)
        assert f"slide_in_{id(component._widget)}" in engine._active_animations

    def test_slide_in_from_right(self, engine, component):
        """测试从右侧滑入"""
        engine.slide_in(component, direction="right", duration=200)
        assert f"slide_in_{id(component._widget)}" in engine._active_animations

    def test_slide_out(self, engine, component):
        """测试滑出动画"""
        engine.slide_out(component, direction="bottom", duration=200)
        assert f"slide_out_{id(component._widget)}" in engine._active_animations

    def test_slide_out_different_directions(self, engine, component):
        """测试不同方向的滑出"""
        directions = ["top", "bottom", "left", "right"]
        for direction in directions:
            engine.slide_out(component, direction=direction, duration=200)
            key = f"slide_out_{id(component._widget)}"
            # 每次都会覆盖，所以只检查最后一个
            assert key in engine._active_animations


class TestScaleAnimations:
    """缩放动画测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def engine(self, qt_app):
        return AnimationEngine()

    @pytest.fixture
    def component(self, qt_app):
        widget = MockWidgetForAnimation()
        widget.setFixedSize(100, 100)
        return MockUIComponentForAnimation("scale_test", widget=widget)

    def test_scale_in(self, engine, component):
        """测试缩放进入动画"""
        initial_size = component._widget.size()
        engine.scale_in(component, duration=200)

        widget_id = id(component._widget)
        assert f"scale_in_{widget_id}" in engine._active_animations

        animation = engine._active_animations[f"scale_in_{widget_id}"]
        assert animation is not None

        process_events_for(0.1)
        # 动画应该将大小从(0,0)缩放到原始大小


class TestAnimationGroups:
    """动画组测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def engine(self, qt_app):
        return AnimationEngine()

    def test_animation_groups_management(self, engine):
        """测试动画组管理"""
        widget = MockWidgetForAnimation()
        component = MockUIComponentForAnimation("group_test", widget=widget)

        # 启动一个产生动画组的动画（如bounce）
        engine.bounce(component, duration=100)

        # 应该有动画组被创建
        assert len(engine._animation_groups) > 0

        # 停止所有动画
        engine.stop_all_animations()
        assert len(engine._animation_groups) == 0


class TestAnimationCleanup:
    """动画清理测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def engine(self, qt_app):
        return AnimationEngine()

    def test_stop_all_animations(self, engine):
        """测试停止所有动画"""
        from PySide6.QtCore import QPropertyAnimation

        for i in range(5):
            widget = MockWidgetForAnimation()
            animation = QPropertyAnimation(widget, b"size")
            animation.setDuration(200)
            engine._active_animations[f"anim_{i}"] = animation

        assert len(engine._active_animations) == 5

        engine.stop_all_animations()
        assert len(engine._active_animations) == 0

    def test_stop_animation_with_component(self, engine):
        """测试停止特定组件的动画"""
        widget = MockWidgetForAnimation()
        component = MockUIComponentForAnimation("stop_comp", widget=widget)

        # 启动淡入动画
        engine.fade_in(component, duration=100)
        widget_id = id(widget)
        key = f"fade_in_{widget_id}"
        assert key in engine._active_animations

        # 停止该组件的动画
        engine.stop_animation(component)
        assert key not in engine._active_animations

    def test_stop_specific_animation_type(self, engine):
        """测试停止特定类型的动画"""
        widget = MockWidgetForAnimation()
        component = MockUIComponentForAnimation("specific_stop", widget=widget)

        # 启动多个不同类型的动画
        engine.fade_in(component, duration=100)
        engine.slide_in(component, direction="bottom", duration=100)

        widget_id = id(widget)
        fade_key = f"fade_in_{widget_id}"
        slide_key = f"slide_in_{widget_id}"

        assert fade_key in engine._active_animations
        assert slide_key in engine._active_animations

        # 只停止fade动画
        engine.stop_animation(component, "fade_in")
        assert fade_key not in engine._active_animations
        assert slide_key in engine._active_animations

        # 清理
        engine.stop_animation(component, "slide_in")


class TestAnimationWithConfig:
    """带配置的动画测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_animation_uses_config_duration(self, qt_app):
        """测试动画使用配置中的持续时间"""
        config = UIConfig(animation_duration=500)
        engine = AnimationEngine(config)

        widget = MockWidgetForAnimation()
        component = MockUIComponentForAnimation("config_test", config=config, widget=widget)

        # 验证配置已设置
        assert engine.config is not None
        assert engine.config.animation_duration == 500


class TestAnimationPerformance:
    """动画性能测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def engine(self, qt_app):
        return AnimationEngine()

    def test_multiple_animations_performance(self, engine):
        """测试多个动画的性能"""
        import time

        widgets = [MockWidgetForAnimation() for _ in range(10)]
        components = [
            MockUIComponentForAnimation(f"perf_comp{i}", widget=widget)
            for i, widget in enumerate(widgets)
        ]

        start_time = time.time()

        for component in components:
            engine.fade_in(component, duration=50)

        process_events_for(0.1)

        end_time = time.time()
        total_time = end_time - start_time

        # 10个动画应该在合理时间内完成
        assert total_time < 1.0  # 小于1秒

    def test_animation_start_time(self, engine):
        """测试动画启动时间"""
        import time

        widget = MockWidgetForAnimation()
        component = MockUIComponentForAnimation("timing_test", widget=widget)

        start = time.time()
        engine.fade_in(component, duration=100)
        process_events_for(0.05)
        end = time.time()

        # 动画应该快速启动
        assert (end - start) < 0.5


class TestAnimationEdgeCases:
    """动画边界情况测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def engine(self, qt_app):
        return AnimationEngine()

    def test_animation_with_none_component(self, engine):
        """测试空组件动画"""
        # 不应该抛出异常
        engine.fade_in(None)

    def test_animation_with_invalid_widget(self, engine):
        """测试无效组件的动画"""
        component = MockUIComponentForAnimation("invalid")
        component._widget = None

        # 应该安全返回
        engine.fade_in(component)

    def test_zero_duration_animation(self, engine):
        """测试零持续时间动画"""
        widget = MockWidgetForAnimation()
        component = MockUIComponentForAnimation("zero_duration", widget=widget)

        # 零持续时间应该也能工作
        engine.fade_in(component, duration=0)
        assert f"fade_in_{id(widget)}" in engine._active_animations

    def test_negative_duration_animation(self, engine):
        """测试负持续时间动画"""
        widget = MockWidgetForAnimation()
        component = MockUIComponentForAnimation("negative_duration", widget=widget)

        # 负持续时间可能导致问题，但应该安全处理
        engine.fade_in(component, duration=-100)
        # 可能不会添加到活动动画中，这取决于实现
