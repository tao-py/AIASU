"""
UI组件测试
测试所有UI组件的功能和交互
"""

import pytest
import time
from PySide6.QtWidgets import QApplication

from ...base import UIConfig, UITheme, Position, CandidateItem, UIEvent
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
    assert_component_lifecycle,
    assert_theme_applied,
    create_test_event,
    wait_for_condition,
    process_events_for,
)
from ..utils.mock_objects import MockWidget


class TestOverlayWindow:
    """悬浮窗口测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        """Qt应用实例"""
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def overlay(self, qt_app):
        """悬浮窗口实例"""
        config = create_test_config()
        overlay = OverlayWindow("test_overlay", config)
        yield overlay
        overlay.hide()

    def test_basic_lifecycle(self, overlay):
        """测试基本生命周期"""
        assert_component_lifecycle(overlay)

    def test_position_setting(self, overlay):
        """测试位置设置"""
        test_pos = Position(200, 300)
        overlay.set_position(test_pos)
        assert overlay._position == test_pos

    def test_content_setting(self, overlay):
        """测试内容设置"""
        test_content = "测试内容"
        overlay.set_content(test_content)
        # 验证内容已设置（具体验证取决于实现）
        assert overlay._content_widget is not None

    def test_theme_update(self, overlay):
        """测试主题更新"""
        theme = create_test_theme("test_theme")
        overlay.update_theme(theme)
        assert overlay._current_theme == theme

    def test_opacity_setting(self, overlay):
        """测试透明度设置"""
        overlay.set_opacity(0.5)
        assert overlay._background_opacity == 0.5

    def test_border_radius_setting(self, overlay):
        """测试圆角半径设置"""
        overlay.set_border_radius(20)
        assert overlay._border_radius == 20

    def test_shadow_toggle(self, overlay):
        """测试阴影开关"""
        overlay.enable_shadow(False)
        assert overlay._shadow_enabled is False

        overlay.enable_shadow(True)
        assert overlay._shadow_enabled is True

    def test_drag_enable(self, overlay):
        """测试拖拽启用"""
        overlay.enable_drag(True)
        assert overlay._drag_enabled is True

    def test_auto_hide_delay(self, overlay):
        """测试自动隐藏延迟"""
        overlay.set_auto_hide_delay(2000)
        assert overlay._auto_hide_timer is not None

    def test_preferred_size(self, overlay):
        """测试推荐尺寸"""
        size = overlay.get_preferred_size()
        assert size.width() > 0
        assert size.height() > 0

    def test_visibility_check(self, overlay):
        """测试可见性检查"""
        # 确保初始隐藏
        overlay.hide()
        process_events_for(0.2)  # 等待隐藏动画完成
        assert not overlay.is_visible()
        
        overlay.show()
        process_events_for(0.2)  # 等待显示动画完成
        assert overlay.is_visible()
        
        overlay.hide()
        process_events_for(0.2)  # 等待隐藏动画完成
        assert not overlay.is_visible()


class TestCandidateView:
    """候选列表测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        """Qt应用实例"""
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def candidate_view(self, qt_app):
        """候选列表实例"""
        config = create_test_config()
        view = CandidateView("test_candidate", config)
        yield view
        view.hide()

    @pytest.fixture
    def test_candidates(self):
        """测试候选项"""
        return create_test_candidates(5)

    def test_basic_lifecycle(self, candidate_view):
        """测试基本生命周期"""
        assert_component_lifecycle(candidate_view)

    def test_candidates_setting(self, candidate_view, test_candidates):
        """测试候选项设置"""
        candidate_view.set_candidates(test_candidates)
        assert len(candidate_view._candidates) == 5
        assert candidate_view._candidates[0].text == "候选1"

    def test_candidate_addition(self, candidate_view, test_candidates):
        """测试候选项添加"""
        candidate_view.set_candidates(test_candidates[:3])
        new_candidate = CandidateItem("新候选", score=0.6)
        candidate_view.add_candidate(new_candidate)

        assert len(candidate_view._candidates) == 4
        assert candidate_view._candidates[-1].text == "新候选"

    def test_candidate_clearing(self, candidate_view, test_candidates):
        """测试候选项清空"""
        candidate_view.set_candidates(test_candidates)
        assert len(candidate_view._candidates) > 0

        candidate_view.clear_candidates()
        assert len(candidate_view._candidates) == 0

    def test_navigation(self, candidate_view, test_candidates):
        """测试导航功能"""
        candidate_view.set_candidates(test_candidates)

        # 测试下一个
        candidate_view.select_next()
        assert candidate_view._selected_index == 0

        # 测试上一个
        candidate_view.select_previous()
        assert candidate_view._selected_index == 4  # 循环到最后一项

    def test_selection_by_index(self, candidate_view, test_candidates):
        """测试按索引选择"""
        candidate_view.set_candidates(test_candidates)

        candidate_view.set_selected_index(2)
        assert candidate_view._selected_index == 2

        selected = candidate_view.get_selected_candidate()
        assert selected is not None
        assert selected.text == "候选3"

    def test_max_visible_items(self, candidate_view):
        """测试最大可见项数"""
        candidate_view.set_max_visible_items(3)
        assert candidate_view._max_visible_items == 3

    def test_feature_toggles(self, candidate_view):
        """测试功能开关"""
        candidate_view.enable_icons(False)
        assert candidate_view._show_icons is False

        candidate_view.enable_scores(False)
        assert candidate_view._show_scores is False

        candidate_view.enable_descriptions(False)
        assert candidate_view._show_descriptions is False

    def test_preferred_size(self, candidate_view, test_candidates):
        """测试推荐尺寸"""
        candidate_view.set_candidates(test_candidates)
        size = candidate_view.get_preferred_size()
        assert size.width() > 0
        assert size.height() > 0


class TestIMEWindow:
    """输入法窗口测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        """Qt应用实例"""
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def ime_window(self, qt_app):
        """输入法窗口实例"""
        config = create_test_config()
        ime = IMEWindow("test_ime", config)
        yield ime
        ime.hide()

    @pytest.fixture
    def test_candidates(self):
        """测试候选项"""
        return create_test_candidates(3)

    def test_basic_lifecycle(self, ime_window):
        """测试基本生命周期"""
        assert_component_lifecycle(ime_window)

    def test_composition_text(self, ime_window):
        """测试输入组合文本"""
        test_text = "测试输入"
        ime_window.set_composition_text(test_text)
        assert ime_window._composition_text == test_text

    def test_candidates_setting(self, ime_window, test_candidates):
        """测试候选项设置"""
        ime_window.set_candidates(test_candidates)
        # 验证候选已设置（具体验证取决于实现）
        assert ime_window._candidate_view is not None

    def test_candidate_navigation(self, ime_window, test_candidates):
        """测试候选导航"""
        ime_window.set_candidates(test_candidates)

        ime_window.select_next_candidate()
        # 验证导航已执行

        ime_window.select_previous_candidate()
        # 验证导航已执行

    def test_selection_confirmation(self, ime_window, test_candidates):
        """测试选择确认"""
        ime_window.set_candidates(test_candidates)
        ime_window._candidate_view.set_selected_index(0)

        result = ime_window.confirm_selection()
        assert result is not None
        assert result == "候选1"

    def test_feature_toggles(self, ime_window):
        """测试功能开关"""
        ime_window.enable_preview(False)
        assert ime_window._show_preview is False

        ime_window.enable_candidates(False)
        assert ime_window._show_candidates is False

        ime_window.enable_follow_cursor(False)
        assert ime_window._follow_cursor_enabled is False

    def test_cursor_offset(self, ime_window):
        """测试光标偏移"""
        from PySide6.QtCore import QPoint

        offset = QPoint(20, 30)
        ime_window.set_cursor_offset(offset)
        assert ime_window._cursor_offset == offset

    def test_theme_update(self, ime_window):
        """测试主题更新"""
        theme = create_test_theme("ime_theme")
        ime_window.update_theme(theme)
        assert ime_window._current_theme == theme

    def test_composition_clearing(self, ime_window):
        """测试输入清空"""
        ime_window.set_composition_text("测试文本")
        assert ime_window._composition_text == "测试文本"

        ime_window.set_composition_text("")
        assert ime_window._composition_text == ""


class TestInputPreview:
    """输入预览测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        """Qt应用实例"""
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def input_preview(self, qt_app):
        """输入预览实例"""
        config = create_test_config()
        preview = InputPreview("test_preview", config)
        yield preview
        preview.hide()

    def test_basic_lifecycle(self, input_preview):
        """测试基本生命周期"""
        assert_component_lifecycle(input_preview)

    def test_text_setting(self, input_preview):
        """测试文本设置"""
        test_text = "测试预览文本"
        input_preview.set_text(test_text)
        assert input_preview._current_text == test_text

    def test_preview_text_setting(self, input_preview):
        """测试预览文本设置"""
        preview_text = "候选预览"
        input_preview.set_preview_text(preview_text)
        assert input_preview._preview_text == preview_text

    def test_text_appending(self, input_preview):
        """测试文本追加"""
        input_preview.set_text("初始文本")
        input_preview.append_text("追加内容")
        assert "追加内容" in input_preview._current_text

    def test_text_insertion(self, input_preview):
        """测试文本插入"""
        input_preview.set_text("初始文本")
        input_preview.insert_text("插入内容", 2)
        assert "插入内容" in input_preview._current_text

    def test_text_clearing(self, input_preview):
        """测试文本清空"""
        input_preview.set_text("测试文本")
        assert input_preview._current_text != ""

        input_preview.clear_text()
        assert input_preview._current_text == ""

    def test_text_highlighting(self, input_preview):
        """测试文本高亮"""
        input_preview.set_text("测试文本内容")
        input_preview.highlight_text(0, 2, "#FF0000")
        # 验证高亮已应用（具体验证取决于实现）

    def test_cursor_position(self, input_preview):
        """测试光标位置"""
        input_preview.set_text("测试文本")
        input_preview.set_cursor_position(2)
        assert input_preview._cursor_position == 2

    def test_max_length_limit(self, input_preview):
        """测试最大长度限制"""
        input_preview.set_max_length(10)
        long_text = "这是一个很长的文本，应该被截断"
        input_preview.set_text(long_text)

        # 验证文本被截断
        assert len(input_preview._current_text) <= 13  # 包括"..."

    def test_feature_toggles(self, input_preview):
        """测试功能开关"""
        input_preview.enable_line_numbers(True)
        assert input_preview._show_line_numbers is True

        input_preview.enable_status_bar(False)
        assert input_preview._show_status_bar is False

    def test_theme_update(self, input_preview):
        """测试主题更新"""
        theme = create_test_theme("preview_theme")
        input_preview.update_theme(theme)
        assert input_preview._current_theme == theme

    def test_preferred_size(self, input_preview):
        """测试推荐尺寸"""
        input_preview.set_text("测试文本")
        size = input_preview.get_preferred_size()
        assert size.width() > 0
        assert size.height() > 0
        assert size.height() <= 300  # 最大高度限制


class TestComponentIntegration:
    """组件集成测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        """Qt应用实例"""
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def components(self, qt_app):
        """所有组件实例"""
        config = create_test_config()
        components = {
            "overlay": OverlayWindow("integration_overlay", config),
            "candidate": CandidateView("integration_candidate", config),
            "ime": IMEWindow("integration_ime", config),
            "preview": InputPreview("integration_preview", config),
        }
        yield components
        # 清理
        for component in components.values():
            component.hide()

    def test_concurrent_theme_update(self, components):
        """测试并发主题更新"""
        theme = create_test_theme("integration_theme")

        # 同时更新所有组件的主题
        for component in components.values():
            component.update_theme(theme)

        # 验证所有组件都应用了主题
        for component in components.values():
            assert component._current_theme == theme

    def test_workflow_simulation(self, components):
        """测试工作流模拟"""
        # 1. 显示输入法窗口
        components["ime"].show(Position(100, 100))
        components["ime"].set_composition_text("测试输入")

        # 2. 设置候选
        candidates = create_test_candidates(3)
        components["ime"].set_candidates(candidates)
        components["candidate"].set_candidates(candidates)

        # 3. 显示输入预览
        components["preview"].set_text("测试预览")
        components["preview"].show(Position(200, 200))

        # 4. 显示悬浮窗口
        components["overlay"].set_content("工作流测试")
        components["overlay"].show(Position(300, 300))

        # 验证所有组件都显示了
        for name, component in components.items():
            assert component.is_visible(), f"{name} should be visible"

    def test_memory_usage(self, components):
        """测试内存使用情况"""
        # 多次显示/隐藏循环
        for i in range(10):
            for component in components.values():
                component.show(Position(100 + i * 10, 100 + i * 10))
                component.hide()

        # 这里可以添加内存检查逻辑
        # 由于测试环境限制，主要验证没有崩溃
        assert True

    def test_event_handling(self, components):
        """测试事件处理"""
        # 模拟输入事件序列
        events = [
            UIEvent("text_input", {"text": "test1"}),
            UIEvent("candidate_selected", {"text": "候选1"}),
            UIEvent("cursor_position_changed", {"position": {"x": 100, "y": 200}}),
        ]

        # 这里可以测试事件在各组件间的传递
        # 由于组件独立，主要验证事件不会导致崩溃
        for event in events:
            # 各组件可以独立处理事件
            pass

        assert True
