#!/usr/bin/env python3
"""
UI层测试框架和示例
用于验证UI组件的功能和性能
"""

import sys
import time
import threading
from typing import List, Optional
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, QTimer

# 导入UI组件
from .base import UIConfig, UITheme, Position, CandidateItem
from .ui_manager import UIManager, SimpleUIManager
from .overlay_window import OverlayWindow, SimpleOverlayWindow
from .candidate_view import CandidateView, SimpleCandidateView
from .ime_window import IMEWindow, SimpleIMEWindow
from .animation_engine import AnimationEngine, SimpleAnimationEngine
from .theme_engine import ThemeEngine, SimpleThemeEngine
from .config_manager import ConfigManager, SimpleConfigManager
from .input_preview import InputPreview, SimpleInputPreview


class UITestSuite:
    """UI测试套件"""

    def __init__(self):
        self.app = None
        self.test_results = []
        self.current_test = 0

    def setup(self):
        """设置测试环境"""
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)

    def run_all_tests(self) -> List[Dict]:
        """运行所有测试"""
        print("开始UI层测试...")

        tests = [
            self.test_ui_manager,
            self.test_overlay_window,
            self.test_candidate_view,
            self.test_ime_window,
            self.test_animation_engine,
            self.test_theme_engine,
            self.test_config_manager,
            self.test_input_preview,
            self.test_integration,
        ]

        for test_func in tests:
            try:
                print(f"\n运行测试: {test_func.__name__}")
                result = test_func()
                self.test_results.append(result)
                print(f"✓ {test_func.__name__}: {result['status']}")
            except Exception as e:
                result = {
                    "test": test_func.__name__,
                    "status": "FAILED",
                    "error": str(e),
                    "duration": 0,
                }
                self.test_results.append(result)
                print(f"✗ {test_func.__name__}: FAILED - {e}")

        return self.test_results

    def test_ui_manager(self) -> Dict:
        """测试UI管理器"""
        start_time = time.time()

        # 创建UI管理器
        config = UIConfig(theme="default", opacity=0.9)
        ui_manager = UIManager(config)

        # 创建测试组件
        overlay = OverlayWindow("test_overlay", config)
        candidate = CandidateView("test_candidate", config)

        # 注册组件
        ui_manager.register_component(overlay)
        ui_manager.register_component(candidate)

        # 测试基本功能
        assert ui_manager.get_component("test_overlay") == overlay
        assert ui_manager.get_component("test_candidate") == candidate
        assert len(ui_manager.list_components()) == 2

        # 测试事件处理
        test_event = type(
            "UIEvent",
            (),
            {
                "event_type": "text_input",
                "data": {"text": "test"},
                "timestamp": time.time(),
            },
        )()

        ui_manager.process_input_event(test_event)

        # 清理
        ui_manager.cleanup()

        duration = time.time() - start_time
        return {"test": "test_ui_manager", "status": "PASSED", "duration": duration}

    def test_overlay_window(self) -> Dict:
        """测试悬浮窗口"""
        start_time = time.time()

        config = UIConfig(opacity=0.95, enable_animation=False)
        overlay = OverlayWindow("test_overlay", config)

        # 测试基本功能
        overlay.set_position(Position(100, 100))
        overlay.show()

        assert overlay.is_visible()
        assert overlay.get_preferred_size().width() > 0

        overlay.hide()
        assert not overlay.is_visible()

        # 测试主题更新
        theme = UITheme(
            name="test_theme",
            background_color="#FF0000",
            text_color="#00FF00",
            accent_color="#0000FF",
            border_color="#FFFFFF",
            opacity=0.8,
            border_radius=10,
            font_family="Arial",
            font_size=12,
        )

        overlay.update_theme(theme)

        duration = time.time() - start_time
        return {"test": "test_overlay_window", "status": "PASSED", "duration": duration}

    def test_candidate_view(self) -> Dict:
        """测试候选列表"""
        start_time = time.time()

        config = UIConfig(max_candidates=5)
        candidate_view = CandidateView("test_candidate", config)

        # 创建测试候选
        candidates = [
            CandidateItem("测试1", "描述1", score=0.9),
            CandidateItem("测试2", "描述2", score=0.8),
            CandidateItem("测试3", "描述3", score=0.7),
        ]

        candidate_view.set_candidates(candidates)
        candidate_view.show()

        # 测试选择功能
        candidate_view.select_next()
        selected = candidate_view.get_selected_candidate()
        assert selected is not None
        assert selected.text == "测试2"

        candidate_view.hide()

        duration = time.time() - start_time
        return {"test": "test_candidate_view", "status": "PASSED", "duration": duration}

    def test_ime_window(self) -> Dict:
        """测试输入法窗口"""
        start_time = time.time()

        config = UIConfig()
        ime_window = IMEWindow("test_ime", config)

        # 测试输入组合
        ime_window.set_composition_text("测试输入")
        assert ime_window._composition_text == "测试输入"

        # 测试候选设置
        candidates = [
            CandidateItem("候选1", score=0.9),
            CandidateItem("候选2", score=0.8),
        ]
        ime_window.set_candidates(candidates)

        duration = time.time() - start_time
        return {"test": "test_ime_window", "status": "PASSED", "duration": duration}

    def test_animation_engine(self) -> Dict:
        """测试动画引擎"""
        start_time = time.time()

        engine = AnimationEngine()

        # 创建测试组件
        config = UIConfig(enable_animation=True, animation_duration=100)
        overlay = OverlayWindow("test_animation", config)

        # 测试动画（简化版，不实际播放）
        engine.fade_in(overlay, 100)
        engine.fade_out(overlay, 100)
        engine.slide_in(overlay, "bottom", 100)
        engine.slide_out(overlay, "bottom", 100)
        engine.scale_in(overlay, 100)
        engine.bounce(overlay, 150)
        engine.shake(overlay, 150)
        engine.pulse(overlay, 200)

        # 停止所有动画
        engine.stop_all_animations()

        duration = time.time() - start_time
        return {
            "test": "test_animation_engine",
            "status": "PASSED",
            "duration": duration,
        }

    def test_theme_engine(self) -> Dict:
        """测试主题引擎"""
        start_time = time.time()

        engine = ThemeEngine("test_themes")

        # 测试主题加载
        default_theme = engine.load_theme("default")
        assert default_theme.name == "default"

        # 测试主题列表
        themes = engine.list_themes()
        assert len(themes) > 0
        assert "default" in themes

        # 测试自定义主题创建
        custom_theme = engine.create_custom_theme(
            "test_custom", "default", background_color="#123456"
        )
        assert custom_theme.name == "test_custom"
        assert custom_theme.background_color == "#123456"

        duration = time.time() - start_time
        return {"test": "test_theme_engine", "status": "PASSED", "duration": duration}

    def test_config_manager(self) -> Dict:
        """测试配置管理器"""
        start_time = time.time()

        config_manager = ConfigManager("test_config")

        # 测试基本配置操作
        config_manager.set("theme_name", "dark")
        assert config_manager.get("theme_name") == "dark"

        config_manager.set("ui.opacity", 0.8)
        assert config_manager.get("ui.opacity") == 0.8

        # 测试UI配置
        ui_config = config_manager.get_ui_config()
        assert isinstance(ui_config, UIConfig)

        duration = time.time() - start_time
        return {"test": "test_config_manager", "status": "PASSED", "duration": duration}

    def test_input_preview(self) -> Dict:
        """测试输入预览"""
        start_time = time.time()

        config = UIConfig()
        preview = InputPreview("test_preview", config)

        # 测试文本设置
        preview.set_text("测试预览文本")
        assert preview._current_text == "测试预览文本"

        # 测试候选预览
        preview.set_preview_text("候选文本")
        assert preview._preview_text == "候选文本"

        # 测试追加文本
        preview.append_text("追加内容")
        assert "追加内容" in preview._current_text

        # 测试清空
        preview.clear_text()
        assert preview._current_text == ""

        duration = time.time() - start_time
        return {"test": "test_input_preview", "status": "PASSED", "duration": duration}

    def test_integration(self) -> Dict:
        """测试组件集成"""
        start_time = time.time()

        # 创建完整的管理器链
        config_manager = ConfigManager("test_integration")
        theme_engine = ThemeEngine("test_integration_themes")
        animation_engine = AnimationEngine()
        ui_manager = UIManager(config_manager.get_ui_config())

        # 设置依赖关系
        ui_manager.set_theme_manager(theme_engine)
        ui_manager.set_animation_controller(animation_engine)

        # 创建组件
        overlay = OverlayWindow("integration_overlay", config_manager.get_ui_config())
        candidate = CandidateView(
            "integration_candidate", config_manager.get_ui_config()
        )
        ime = IMEWindow("integration_ime", config_manager.get_ui_config())
        preview = InputPreview("integration_preview", config_manager.get_ui_config())

        # 注册组件
        ui_manager.register_component(overlay)
        ui_manager.register_component(candidate)
        ui_manager.register_component(ime)
        ui_manager.register_component(preview)

        # 测试完整工作流程
        # 1. 设置主题
        ui_manager.update_theme("dark")

        # 2. 模拟输入事件
        test_event = type(
            "UIEvent",
            (),
            {
                "event_type": "text_input",
                "data": {"text": "integration_test"},
                "timestamp": time.time(),
            },
        )()

        ui_manager.process_input_event(test_event)

        # 3. 设置候选
        candidates = [
            CandidateItem("集成测试1", score=0.9),
            CandidateItem("集成测试2", score=0.8),
        ]
        candidate.set_candidates(candidates)

        # 4. 设置预览
        preview.set_text("集成测试预览")
        ime.set_composition_text("集成测试输入")

        # 清理
        ui_manager.cleanup()

        duration = time.time() - start_time
        return {"test": "test_integration", "status": "PASSED", "duration": duration}

    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 50)
        print("UI层测试摘要")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "PASSED")
        failed_tests = total_tests - passed_tests

        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")

        if failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if result["status"] == "FAILED":
                    print(
                        f"  - {result['test']}: {result.get('error', 'Unknown error')}"
                    )

        total_duration = sum(r["duration"] for r in self.test_results)
        print(f"\n总耗时: {total_duration:.3f}秒")

        if passed_tests == total_tests:
            print("\n✓ 所有测试通过!")
        else:
            print(f"\n✗ {failed_tests}个测试失败")


class UIDemoWindow(QMainWindow):
    """UI演示窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AIASU UI层演示")
        self.setGeometry(100, 100, 800, 600)

        # 初始化组件
        self.init_ui()
        self.init_managers()

    def init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 创建控制按钮
        buttons = [
            ("显示悬浮窗口", self.show_overlay),
            ("显示候选列表", self.show_candidates),
            ("显示输入法窗口", self.show_ime),
            ("显示输入预览", self.show_preview),
            ("切换主题", self.switch_theme),
            ("播放动画", self.play_animation),
            ("运行测试", self.run_tests),
        ]

        for text, callback in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        # 添加状态标签
        self.status_label = QLabel("准备就绪")
        layout.addWidget(self.status_label)

    def init_managers(self):
        """初始化管理器"""
        # 配置管理器
        self.config_manager = ConfigManager("demo_config")

        # 主题引擎
        self.theme_engine = ThemeEngine("demo_themes")

        # 动画引擎
        self.animation_engine = AnimationEngine()

        # UI管理器
        self.ui_manager = UIManager(self.config_manager.get_ui_config())
        self.ui_manager.set_theme_manager(self.theme_engine)
        self.ui_manager.set_animation_controller(self.animation_engine)

        # 创建组件
        self.overlay = OverlayWindow(
            "demo_overlay", self.config_manager.get_ui_config()
        )
        self.candidate = CandidateView(
            "demo_candidate", self.config_manager.get_ui_config()
        )
        self.ime = IMEWindow("demo_ime", self.config_manager.get_ui_config())
        self.preview = InputPreview("demo_preview", self.config_manager.get_ui_config())

        # 注册组件
        self.ui_manager.register_component(self.overlay)
        self.ui_manager.register_component(self.candidate)
        self.ui_manager.register_component(self.ime)
        self.ui_manager.register_component(self.preview)

        # 连接信号
        self.candidate.candidate_selected.connect(self.on_candidate_selected)
        self.ime.candidate_selected.connect(self.on_candidate_selected)
        self.preview.text_changed.connect(self.on_preview_text_changed)

    def show_overlay(self):
        """显示悬浮窗口"""
        pos = Position(300, 300)
        self.overlay.set_content("这是悬浮窗口的内容\n可以显示多行文本")
        self.ui_manager.show_component("demo_overlay", pos)
        self.status_label.setText("悬浮窗口已显示")

    def show_candidates(self):
        """显示候选列表"""
        pos = Position(400, 400)
        candidates = [
            CandidateItem("候选词1", "这是第一个候选词", score=0.9),
            CandidateItem("候选词2", "这是第二个候选词", score=0.8),
            CandidateItem("候选词3", "这是第三个候选词", score=0.7),
        ]
        self.candidate.set_candidates(candidates)
        self.ui_manager.show_component("demo_candidate", pos)
        self.status_label.setText("候选列表已显示")

    def show_ime(self):
        """显示输入法窗口"""
        pos = Position(500, 500)
        self.ime.set_composition_text("输入法测试")
        candidates = [
            CandidateItem("输入法", score=0.95),
            CandidateItem("输入", score=0.85),
            CandidateItem("法", score=0.75),
        ]
        self.ime.set_candidates(candidates)
        self.ui_manager.show_component("demo_ime", pos)
        self.status_label.setText("输入法窗口已显示")

    def show_preview(self):
        """显示输入预览"""
        pos = Position(600, 300)
        self.preview.set_text("这是输入预览的测试文本\n可以显示多行内容")
        self.preview.set_preview_text("候选：预览, 预演, 预示")
        self.ui_manager.show_component("demo_preview", pos)
        self.status_label.setText("输入预览已显示")

    def switch_theme(self):
        """切换主题"""
        themes = self.theme_engine.list_themes()
        current_theme = self.config_manager.get_theme_name()

        # 找到下一个主题
        try:
            current_index = themes.index(current_theme)
            next_index = (current_index + 1) % len(themes)
            next_theme = themes[next_index]
        except ValueError:
            next_theme = themes[0] if themes else "default"

        self.ui_manager.update_theme(next_theme)
        self.config_manager.set_theme_name(next_theme)
        self.status_label.setText(f"主题已切换到: {next_theme}")

    def play_animation(self):
        """播放动画"""
        # 显示悬浮窗口并播放动画
        self.overlay.set_content("动画测试")
        self.overlay.show()

        # 播放淡入动画
        self.animation_engine.fade_in(self.overlay, 300)

        # 延迟后播放弹跳动画
        QTimer.singleShot(500, lambda: self.animation_engine.bounce(self.overlay, 500))

        self.status_label.setText("动画已播放")

    def run_tests(self):
        """运行测试"""
        self.status_label.setText("正在运行测试...")

        # 创建测试套件
        test_suite = UITestSuite()
        test_suite.setup()

        # 运行测试
        def run_tests_async():
            results = test_suite.run_all_tests()

            # 更新UI
            def update_ui():
                test_suite.print_summary()
                passed = sum(1 for r in results if r["status"] == "PASSED")
                total = len(results)
                self.status_label.setText(f"测试完成: {passed}/{total} 通过")

            # 在主线程更新UI
            QTimer.singleShot(0, update_ui)

        # 在新线程中运行测试
        thread = threading.Thread(target=run_tests_async)
        thread.start()

    def on_candidate_selected(self, text: str):
        """候选选择事件"""
        self.status_label.setText(f"选择了候选: {text}")

    def on_preview_text_changed(self, text: str):
        """预览文本变更事件"""
        print(f"预览文本变更: {text}")

    def closeEvent(self, event):
        """关闭事件"""
        self.ui_manager.cleanup()
        event.accept()


def run_demo():
    """运行演示程序"""
    app = QApplication(sys.argv)

    # 创建演示窗口
    demo = UIDemoWindow()
    demo.show()

    # 运行应用
    sys.exit(app.exec())


def run_tests():
    """运行测试"""
    app = QApplication(sys.argv)

    # 创建测试套件
    test_suite = UITestSuite()
    test_suite.setup()

    # 运行测试
    results = test_suite.run_all_tests()
    test_suite.print_summary()

    # 检查是否有失败的测试
    failed_tests = [r for r in results if r["status"] == "FAILED"]
    if failed_tests:
        sys.exit(1)
    else:
        print("\n所有测试通过!")
        sys.exit(0)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        run_demo()
