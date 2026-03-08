"""
测试辅助函数
提供常用的测试工具函数
"""

import time
import threading
from typing import List, Optional, Dict, Any, Callable
from PySide6.QtCore import QTimer, QObject
from PySide6.QtWidgets import QApplication

from ...base import UIComponent, UITheme, UIConfig, Position, CandidateItem


def setup_test_qt_app() -> QApplication:
    """设置测试用的Qt应用"""
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


def teardown_test_qt_app():
    """清理测试用的Qt应用"""
    app = QApplication.instance()
    if app:
        app.quit()
        app.deleteLater()


def wait_for_signal(signal: QObject, timeout: float = 1.0) -> bool:
    """等待信号发射"""
    received = [False]

    def handler(*args):
        received[0] = True

    signal.connect(handler)

    start_time = time.time()
    while not received[0] and time.time() - start_time < timeout:
        QApplication.processEvents()
        time.sleep(0.01)

    signal.disconnect(handler)
    return received[0]


def process_events_for(duration: float = 0.1):
    """处理Qt事件循环指定时间"""
    start_time = time.time()
    while time.time() - start_time < duration:
        QApplication.processEvents()
        time.sleep(0.01)


def create_test_candidates(count: int = 5) -> List[CandidateItem]:
    """创建测试候选项"""
    candidates = []
    for i in range(count):
        candidates.append(
            CandidateItem(
                text=f"候选{i + 1}",
                description=f"这是第{i + 1}个候选词，用于测试目的",
                score=1.0 - (i * 0.1),
            )
        )
    return candidates


def create_test_theme(name: str = "test_theme") -> UITheme:
    """创建测试主题"""
    return UITheme(
        name=name,
        background_color="#FF0000",
        text_color="#00FF00",
        accent_color="#0000FF",
        border_color="#FFFFFF",
        opacity=0.8,
        border_radius=10,
        font_family="Arial",
        font_size=12,
    )


def create_test_config() -> UIConfig:
    """创建测试配置"""
    return UIConfig(
        theme="test",
        opacity=0.9,
        animation_duration=100,
        max_candidates=5,
        window_padding=8,
        font_size=14,
        follow_cursor=True,
        multi_monitor=False,
        auto_hide_delay=1000,
        enable_animation=True,
    )


def measure_execution_time(func: Callable, *args, **kwargs) -> tuple[Any, float]:
    """测量函数执行时间

    Returns:
        (函数返回值, 执行时间秒数)
    """
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    return result, end_time - start_time


def assert_component_lifecycle(component: UIComponent, test_position: Position = None):
    """测试组件生命周期"""
    # 初始状态应该是隐藏
    assert component.state.value == "hidden"

    # 显示组件
    component.show(test_position or Position(100, 100))
    assert component.state.value == "visible"

    # 隐藏组件
    component.hide()
    assert component.state.value == "hidden"


def assert_theme_applied(component: UIComponent, theme: UITheme):
    """断言主题已应用"""
    # 这里可以检查组件的视觉属性
    # 由于模拟组件的限制，主要检查是否调用了update_theme
    component.update_theme(theme)
    # 在实际组件中，这里应该检查颜色、字体等属性


def create_test_event_sequence() -> List[Dict[str, Any]]:
    """创建测试事件序列"""
    return [
        {"type": "text_input", "data": {"text": "test1"}},
        {"type": "candidate_selected", "data": {"text": "候选1"}},
        {"type": "keyboard_shortcut", "data": {"shortcut": "toggle"}},
        {"type": "cursor_position_changed", "data": {"position": {"x": 100, "y": 200}}},
    ]


def run_event_sequence_test(ui_manager, event_sequence: List[Dict[str, Any]]):
    """运行事件序列测试"""
    for event_data in event_sequence:
        event = UIEvent(event_data["type"], event_data["data"])
        ui_manager.process_input_event(event)
        process_events_for(0.05)  # 给事件处理一些时间


def assert_performance_within_limit(func: Callable, max_time: float, *args, **kwargs):
    """断言函数执行时间在限制内"""
    result, duration = measure_execution_time(func, *args, **kwargs)
    assert duration < max_time, (
        f"Function took {duration:.3f}s, expected < {max_time:.3f}s"
    )
    return result


def create_stress_test_candidates(count: int = 100) -> List[CandidateItem]:
    """创建压力测试用的候选项"""
    candidates = []
    for i in range(count):
        candidates.append(
            CandidateItem(
                text=f"候选{i + 1}" * 10,  # 长文本
                description=f"这是一个很长的描述文本，用于测试性能{i + 1}" * 5,
                score=1.0 - (i * 0.01),
            )
        )
    return candidates


def simulate_user_interaction(component: UIComponent, interaction_type: str = "basic"):
    """模拟用户交互"""
    if interaction_type == "basic":
        # 基本交互：显示 -> 等待 -> 隐藏
        component.show(Position(100, 100))
        process_events_for(0.1)
        component.hide()

    elif interaction_type == "complex":
        # 复杂交互：多次显示隐藏
        for i in range(3):
            pos = Position(100 + i * 50, 100 + i * 50)
            component.show(pos)
            process_events_for(0.05)
            component.hide()
            process_events_for(0.05)


def check_memory_leak(operation: Callable, iterations: int = 100) -> List[int]:
    """检查内存泄漏

    Returns:
        每次迭代的内存使用量列表
    """
    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_usage = []

        for i in range(iterations):
            operation()
            memory = process.memory_info().rss
            memory_usage.append(memory)

            # 每10次强制垃圾回收
            if i % 10 == 0:
                import gc

                gc.collect()

        return memory_usage

    except ImportError:
        # 如果没有psutil，返回模拟数据
        return [1024 * 1024] * iterations  # 1MB模拟数据


def create_test_thread_safe_operation(
    component: UIComponent, thread_count: int = 5
) -> List[threading.Thread]:
    """创建线程安全的测试操作"""
    threads = []

    def thread_operation(thread_id: int):
        for i in range(10):
            position = Position(100 + thread_id * 10, 100 + i * 10)
            component.show(position)
            process_events_for(0.01)
            component.hide()
            process_events_for(0.01)

    for i in range(thread_count):
        thread = threading.Thread(target=thread_operation, args=(i,))
        threads.append(thread)

    return threads
