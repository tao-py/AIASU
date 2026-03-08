"""
测试辅助工具
提供测试用的模拟对象和辅助函数
"""

import time
from typing import List, Optional, Dict, Any
from PySide6.QtCore import QObject, Signal, QPoint
from PySide6.QtWidgets import QWidget

from ...base import (
    UIComponent,
    WindowComponent,
    UITheme,
    UIConfig,
    Position,
    CandidateItem,
    UIEvent,
)


class MockWidget(QWidget):
    """模拟的QWidget，用于测试"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._visible = False
        self._pos = QPoint(0, 0)
        self._size = (100, 100)
        self._opacity = 1.0

    def show(self):
        self._visible = True

    def hide(self):
        self._visible = False

    def isVisible(self) -> bool:
        return self._visible

    def move(self, x: int, y: int):
        self._pos = QPoint(x, y)

    def pos(self) -> QPoint:
        return self._pos

    def size(self):
        return type(
            "Size",
            (),
            {"width": lambda: self._size[0], "height": lambda: self._size[1]},
        )()

    def setWindowOpacity(self, opacity: float):
        self._opacity = opacity

    def windowOpacity(self) -> float:
        return self._opacity


class MockUIComponent(UIComponent):
    """模拟的UI组件，用于测试"""

    def __init__(self, name: str = "mock", config: Optional[UIConfig] = None):
        super().__init__(name, config or UIConfig())
        self._widget = MockWidget()
        self._visible = False
        self._theme = None
        self._position = Position(0, 0)

    def show(self, position: Optional[Position] = None) -> None:
        self._visible = True
        self.set_state(type("UIState", (), {"VISIBLE": "visible"})().VISIBLE)
        if position:
            self._position = position

    def hide(self) -> None:
        self._visible = False
        self.set_state(type("UIState", (), {"HIDDEN": "hidden"})().HIDDEN)

    def update_theme(self, theme: UITheme) -> None:
        self._theme = theme

    def get_preferred_size(self):
        return type("Size", (), {"width": lambda: 200, "height": lambda: 100})()

    def is_visible(self) -> bool:
        return self._visible


class MockWindowComponent(WindowComponent):
    """模拟的窗口组件，用于测试"""

    def __init__(self, name: str = "mock_window", config: Optional[UIConfig] = None):
        super().__init__(name, config or UIConfig())
        self._window = MockWidget()
        self._content_widget = MockWidget()

    def create_window(self) -> None:
        pass

    def set_position(self, position: Position) -> None:
        if self._window:
            self._window.move(position.x, position.y)

    def set_content(self, content: Any) -> None:
        pass

    def show(self, position: Optional[Position] = None) -> None:
        super().show(position)
        if self._window:
            self._window.show()

    def hide(self) -> None:
        super().hide()
        if self._window:
            self._window.hide()


class MockTheme:
    """模拟的主题"""

    @staticmethod
    def create_default() -> UITheme:
        return UITheme(
            name="default",
            background_color="#1C1C1E",
            text_color="#FFFFFF",
            accent_color="#007AFF",
            border_color="#3A3A3C",
            opacity=0.95,
            border_radius=12,
            font_family="Arial",
            font_size=14,
        )

    @staticmethod
    def create_dark() -> UITheme:
        return UITheme(
            name="dark",
            background_color="#000000",
            text_color="#FFFFFF",
            accent_color="#0A84FF",
            border_color="#38383A",
            opacity=0.98,
            border_radius=10,
            font_family="Arial",
            font_size=14,
        )


class MockConfig:
    """模拟的配置"""

    @staticmethod
    def create_default() -> UIConfig:
        return UIConfig(
            theme="default",
            opacity=0.95,
            animation_duration=200,
            max_candidates=5,
            window_padding=8,
            font_size=14,
            follow_cursor=True,
            multi_monitor=True,
            auto_hide_delay=3000,
            enable_animation=True,
        )

    @staticmethod
    def create_simple() -> UIConfig:
        return UIConfig(
            theme="default",
            opacity=1.0,
            animation_duration=0,
            max_candidates=3,
            window_padding=5,
            font_size=12,
            follow_cursor=False,
            multi_monitor=False,
            auto_hide_delay=0,
            enable_animation=False,
        )


class MockCandidate:
    """模拟的候选项"""

    @staticmethod
    def create_list(count: int = 5) -> List[CandidateItem]:
        candidates = []
        for i in range(count):
            candidates.append(
                CandidateItem(
                    text=f"候选{i + 1}",
                    description=f"这是第{i + 1}个候选词",
                    score=1.0 - (i * 0.1),
                )
            )
        return candidates

    @staticmethod
    def create_single(text: str = "测试候选", score: float = 0.9) -> CandidateItem:
        return CandidateItem(text=text, description=f"这是{text}的描述", score=score)


class Timer:
    """简单的计时器，用于性能测试"""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()

    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


class MemoryTracker:
    """内存使用追踪器"""

    def __init__(self):
        self.initial_memory = None
        self.peak_memory = None

    def start(self):
        """开始追踪内存使用"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        self.initial_memory = process.memory_info().rss
        self.peak_memory = self.initial_memory

    def check(self):
        """检查当前内存使用"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        current_memory = process.memory_info().rss

        if current_memory > self.peak_memory:
            self.peak_memory = current_memory

        return current_memory

    @property
    def memory_increase(self) -> int:
        """获取内存增长量（字节）"""
        if self.initial_memory and self.peak_memory:
            return self.peak_memory - self.initial_memory
        return 0


def create_test_event(event_type: str, data: Dict[str, Any] = None) -> UIEvent:
    """创建测试事件"""
    return UIEvent(event_type, data or {})


def wait_for_condition(
    condition_func, timeout: float = 1.0, interval: float = 0.1
) -> bool:
    """等待条件满足"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)

    return False


def assert_component_state(component: UIComponent, expected_state: str):
    """断言组件状态"""
    assert component.state.value == expected_state, (
        f"Expected state {expected_state}, got {component.state.value}"
    )


def assert_position_equal(pos1: Position, pos2: Position, tolerance: int = 1):
    """断言位置相等（允许误差）"""
    assert abs(pos1.x - pos2.x) <= tolerance, (
        f"X position mismatch: {pos1.x} != {pos2.x}"
    )
    assert abs(pos1.y - pos2.y) <= tolerance, (
        f"Y position mismatch: {pos1.y} != {pos2.y}"
    )


def create_mock_animation_callback():
    """创建模拟动画回调"""
    callback_data = {"called": False, "args": None}

    def callback(*args):
        callback_data["called"] = True
        callback_data["args"] = args

    return callback, callback_data
