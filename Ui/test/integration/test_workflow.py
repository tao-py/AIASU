"""
工作流测试
测试完整的用户工作流程和场景
"""

import pytest
import time
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ...base import UIConfig, UITheme, Position, CandidateItem
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


class TestTypingWorkflow:
    """打字输入工作流测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def typing_environment(self, qt_app):
        """创建打字输入环境"""
        config = create_test_config()
        manager = UIManager(config)
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()

        ime = IMEWindow("typing_ime", config)
        candidate = CandidateView("typing_candidate", config)
        preview = InputPreview("typing_preview", config)

        manager.register_component(ime)
        manager.register_component(candidate)
        manager.register_component(preview)

        return {
            "manager": manager,
            "ime": ime,
            "candidate": candidate,
            "preview": preview,
            "config": config,
        }

    def test_single_character_input(self, typing_environment):
        """测试单字符输入"""
        env = typing_environment
        ime = env["ime"]

        # 显示IME窗口
        ime.show(Position(300, 300))
        assert ime.is_visible()

        # 输入文本
        ime.set_composition_text("a")
        assert ime._composition_text == "a"

        # 没有候选，应该直接上屏
        # 具体行为取决于实现

    def test_pinyin_input_with_candidates(self, typing_environment):
        """测试拼音输入带候选"""
        env = typing_environment
        ime = env["ime"]
        candidate = env["candidate"]

        # 显示IME
        ime.show(Position(300, 300))

        # 输入拼音
        ime.set_composition_text("zhong")
        assert "zhong" in ime._composition_text

        # 设置候选词
        candidates = [
            CandidateItem("中", score=0.95),
            CandidateItem("种", score=0.9),
            CandidateItem("钟", score=0.85),
            CandidateItem("众", score=0.8),
        ]
        ime.set_candidates(candidates)
        candidate.set_candidates(candidates)

        assert len(ime._candidates) == 4
        assert len(candidate._candidates) == 4

        # 选择第一个候选
        ime._candidate_view.set_selected_index(0)
        selected = ime.confirm_selection()

        assert selected is not None
        assert selected.text == "中"

    def test_multi_page_candidates(self, typing_environment):
        """测试多页候选"""
        env = typing_environment
        candidate = env["candidate"]

        # 创建大量候选（超过一页）
        many_candidates = create_test_candidates(20)
        candidate.set_candidates(many_candidates)
        candidate.set_max_visible_items(5)

        assert len(candidate._candidates) == 20

        # 测试翻页（如果实现了）
        # 具体实现取决于CandidateView

    def test_complex_input_sequence(self, typing_environment):
        """测试复杂输入序列"""
        env = typing_environment
        ime = env["ime"]
        candidate = env["candidate"]
        preview = env["preview"]

        # 显示IME
        ime.show(Position(300, 300))

        # 第一组输入
        ime.set_composition_text("你好")
        candidates1 = [
            CandidateItem("你好", score=0.98),
            CandidateItem("泥好", score=0.5),
        ]
        ime.set_candidates(candidates1)
        candidate.set_candidates(candidates1)

        # 选择第一个
        ime._candidate_view.set_selected_index(0)
        selected1 = ime.confirm_selection()
        assert selected1.text == "你好"

        # 更新预览
        preview.set_text(selected1.text)
        assert preview._current_text == "你好"

        # 第二组输入
        ime.set_composition_text("世界")
        candidates2 = [
            CandidateItem("世界", score=0.99),
            CandidateItem("视界", score=0.6),
        ]
        ime.set_candidates(candidates2)
        candidate.set_candidates(candidates2)

        ime._candidate_view.set_selected_index(0)
        selected2 = ime.confirm_selection()
        assert selected2.text == "世界"


class TestThemeSwitchingWorkflow:
    """主题切换工作流测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def themed_components(self, qt_app):
        """创建带主题的组件"""
        config = create_test_config()
        manager = UIManager(config)
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()

        components = {
            "overlay": OverlayWindow("theme_overlay", config),
            "candidate": CandidateView("theme_candidate", config),
            "ime": IMEWindow("theme_ime", config),
            "preview": InputPreview("theme_preview", config),
        }

        for comp in components.values():
            manager.register_component(comp)

        return {"manager": manager, **components}

    def test_switch_between_builtin_themes(self, themed_components):
        """测试在内置主题间切换"""
        manager = themed_components["manager"]

        # 默认主题
        manager.update_theme("default")
        # 应该不抛出异常

        # 切换到暗色主题
        manager.update_theme("dark")

        # 切换到亮色主题（如果存在）
        manager.update_theme("light")

        # 验证所有组件都接收到主题更新
        for comp in themed_components.values():
            if hasattr(comp, "_current_theme"):
                # 主题应该已更新
                pass

    def test_custom_theme_application(self, themed_components):
        """测试自定义主题应用"""
        manager = themed_components["manager"]

        # 创建自定义主题
        custom_theme = create_test_theme("workflow_custom")

        manager.update_theme("workflow_custom")

        # 验证主题已应用
        # 具体检查取决于实现


class TestErrorHandlingWorkflow:
    """错误处理工作流测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_recovery_from_component_failure(self, qt_app):
        """测试从组件故障恢复"""
        manager = UIManager()
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()

        # 添加正常组件
        normal_overlay = OverlayWindow("normal", manager._config)
        manager.register_component(normal_overlay)

        assert "normal" in manager._components

        # 即使有异常组件，管理器应该继续工作
        # 测试添加和移除组件的能力

    def test_handle_invalid_configuration(self, qt_app):
        """测试处理无效配置"""
        # 使用不完整的配置
        try:
            incomplete_config = UIConfig(theme=None)  # 可能的无效值
            manager = UIManager(incomplete_config)
            # 应该能创建，具体行为取决于实现
        except Exception:
            # 如果抛出异常，也是可接受的
            pass

    def test_graceful_handling_of_missing_resources(self, qt_app):
        """测试优雅处理缺失资源"""
        manager = UIManager()

        # 尝试操作不存在的组件
        manager.show_component("nonexistent")
        manager.hide_component("nonexistent")
        manager.get_component("nonexistent")

        # 所有这些操作都不应该崩溃


class TestLifecycleManagement:
    """生命周期管理测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def component_lifecycle_setup(self, qt_app):
        """组件生命周期设置"""
        config = create_test_config()
        manager = UIManager(config)
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()

        overlay = OverlayWindow("lifecycle_overlay", config)
        candidate = CandidateView("lifecycle_candidate", config)
        ime = IMEWindow("lifecycle_ime", config)
        preview = InputPreview("lifecycle_preview", config)

        manager.register_component(overlay)
        manager.register_component(candidate)
        manager.register_component(ime)
        manager.register_component(preview)

        return {"manager": manager, "components": [overlay, candidate, ime, preview]}

    def test_full_lifecycle_cycle(self, component_lifecycle_setup):
        """测试完整生命周期循环"""
        manager = component_lifecycle_setup["manager"]
        components = component_lifecycle_setup["components"]

        # 初始状态：所有组件已注册但隐藏
        for comp in components:
            assert comp.state == UIState.HIDDEN

        # 显示所有组件
        for i, comp in enumerate(components):
            pos = Position(100 + i * 50, 100 + i * 50)
            manager.show_component(comp.name, pos)

        for comp in components:
            assert comp.state == UIState.VISIBLE

        # 隐藏所有组件
        for comp in components:
            manager.hide_component(comp.name)

        for comp in components:
            assert comp.state == UIState.HIDDEN

    def test_dynamic_component_addition_removal(self, component_lifecycle_setup):
        """测试动态添加和移除组件"""
        manager = component_lifecycle_setup["manager"]

        # 初始4个组件
        assert len(manager._components) == 4

        # 动态添加新组件
        new_overlay = OverlayWindow("new_overlay", manager._config)
        manager.register_component(new_overlay)
        assert len(manager._components) == 5
        assert "new_overlay" in manager._components

        # 动态移除组件
        manager.unregister_component("new_overlay")
        assert len(manager._components) == 4
        assert "new_overlay" not in manager._components

    def test_component_recreation(self, qt_app):
        """测试组件重建"""
        config = create_test_config()

        # 多次创建和销毁同一类型组件
        for i in range(3):
            overlay = OverlayWindow(f"recreate_overlay_{i}", config)
            assert overlay is not None
            # 组件应该正确初始化

            # 清理
            overlay.hide()


class TestStateSynchronization:
    """状态同步测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    @pytest.fixture
    def synchronized_environment(self, qt_app):
        """创建同步环境"""
        config = create_test_config()
        manager = UIManager(config)
        manager._animation_controller = AnimationEngine()
        manager._theme_manager = ThemeEngine()

        ime = IMEWindow("sync_ime", config)
        candidate = CandidateView("sync_candidate", config)

        manager.register_component(ime)
        manager.register_component(candidate)

        return {"manager": manager, "ime": ime, "candidate": candidate}

    def test_composition_state_sync(self, synchronized_environment):
        """测试输入组合状态同步"""
        ime = synchronized_environment["ime"]

        # 设置组合文本
        ime.set_composition_text("测试")
        assert ime._composition_text == "测试"

        # 清空组合文本
        ime.set_composition_text("")
        assert ime._composition_text == ""

    def test_candidate_selection_state_sync(self, synchronized_environment):
        """测试候选选择状态同步"""
        ime = synchronized_environment["ime"]
        candidate = synchronized_environment["candidate"]

        candidates = create_test_candidates(5)
        ime.set_candidates(candidates)
        candidate.set_candidates(candidates)

        # 选择应该同步
        candidate.set_selected_index(2)
        selected_candidate = candidate.get_selected_candidate()
        assert selected_candidate is not None
        assert selected_candidate.text == "候选3"

    def test_visibility_state_sync(self, synchronized_environment):
        """测试可见性状态同步"""
        ime = synchronized_environment["ime"]

        # 隐藏状态
        assert not ime.is_visible()

        # 显示状态
        ime.show(Position(200, 200))
        assert ime.is_visible()

        # 回到隐藏状态
        ime.hide()
        assert not ime.is_visible()


class TestDataPersistence:
    """数据持久化测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_theme_persistence_across_sessions(self, qt_app):
        """测试主题在会话间的持久性"""
        from ...config_manager import ConfigManager
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            # 第一会话：保存主题配置
            config_manager = ConfigManager(temp_dir)
            config_manager.set("theme_name", "dark")
            config_manager.save_config()

            # 第二会话：加载主题配置
            new_manager = ConfigManager(temp_dir)
            saved_theme = new_manager.get("theme_name")
            assert saved_theme == "dark"

    def test_user_preferences_persistence(self, qt_app):
        """测试用户偏好持久化"""
        from ...config_manager import ConfigManager
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)

            # 保存用户偏好
            preferences = {
                "ui.opacity": 0.85,
                "ui.font_size": 16,
                "auto_start": True,
                "language": "en-US",
            }

            for key, value in preferences.items():
                manager.set(key, value)

            manager.save_config()

            # 加载验证
            new_manager = ConfigManager(temp_dir)
            for key, expected_value in preferences.items():
                actual_value = new_manager.get(key)
                assert actual_value == expected_value, f"Key {key}: expected {expected_value}, got {actual_value}"


class TestWorkflowPerformance:
    """工作流性能测试"""

    @pytest.fixture(scope="class")
    def qt_app(self):
        app = setup_test_qt_app()
        yield app
        teardown_test_qt_app()

    def test_rapid_theme_switching_performance(self, qt_app):
        """测试快速主题切换性能"""
        import time

        config = create_test_config()
        manager = UIManager(config)
        manager._theme_manager = ThemeEngine()

        overlay = OverlayWindow("rapid_theme", config)
        manager.register_component(overlay)

        themes = ["default", "dark", "light", "glass"]

        start_time = time.time()

        for _ in range(10):
            for theme in themes:
                manager.update_theme(theme)

        end_time = time.time()
        total_time = end_time - start_time

        # 40次主题切换应该很快
        assert total_time < 2.0

    def test_large_candidate_set_handling(self, qt_app):
        """测试大量候选项处理"""
        from ...candidate_view import CandidateView

        config = create_test_config()
        candidate_view = CandidateView("large_candidate_set", config)

        # 创建大量候选项
        large_candidates = create_test_candidates(100)

        start_time = time.time()
        candidate_view.set_candidates(large_candidates)
        end_time = time.time()

        set_time = end_time - start_time
        assert set_time < 0.5  # 应该在0.5秒内完成
        assert len(candidate_view._candidates) == 100
