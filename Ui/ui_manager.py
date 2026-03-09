from typing import Dict, Optional, List, Any, Callable
from PySide6.QtCore import QObject, Signal, QTimer, QThread, QSize
from PySide6.QtWidgets import QApplication
import threading
import time

from .base import (
    UIComponent,
    UIManagerInterface,
    UIEvent,
    UITheme,
    UIConfig,
    Position,
    UIState,
    AnimationController,
    ThemeManager,
    PositionManager,
    QObjectABCMeta
)


class UIManager(QObject, UIManagerInterface, metaclass=QObjectABCMeta):
    """UI管理器 - 统一管理所有UI组件"""

    # 定义信号
    component_registered = Signal(str)  # 组件注册信号
    component_unregistered = Signal(str)  # 组件注销信号
    theme_changed = Signal(str)  # 主题变更信号
    input_event_received = Signal(UIEvent)  # 输入事件信号

    def __init__(self, config: Optional[UIConfig] = None):
        super().__init__()
        self._components: Dict[str, UIComponent] = {}
        self._config = config or UIConfig()
        self._animation_controller: Optional[AnimationController] = None
        self._theme_manager: Optional[ThemeManager] = None
        self._position_manager: Optional[PositionManager] = None
        self._event_queue: List[UIEvent] = []
        self._is_processing_events = False
        self._auto_hide_timers: Dict[str, QTimer] = {}
        self._main_thread_id = threading.current_thread().ident

    def register_component(self, component: UIComponent) -> None:
        """注册UI组件"""
        if component.name in self._components:
            print(f"Warning: Component {component.name} already registered")
            return

        self._components[component.name] = component

        # 连接组件事件
        component.add_event_handler("state_changed", self._on_component_state_changed)
        component.add_event_handler(
            "position_changed", self._on_component_position_changed
        )

        self.component_registered.emit(component.name)
        print(f"Component registered: {component.name}")

    def unregister_component(self, component_name: str) -> None:
        """注销UI组件"""
        if component_name not in self._components:
            return

        # 停止自动隐藏定时器
        if component_name in self._auto_hide_timers:
            self._auto_hide_timers[component_name].stop()
            del self._auto_hide_timers[component_name]

        del self._components[component_name]
        self.component_unregistered.emit(component_name)
        print(f"Component unregistered: {component_name}")

    def show_component(
        self, component_name: str, position: Optional[Position] = None
    ) -> None:
        """显示组件"""
        component = self.get_component(component_name)
        if not component:
            print(f"Error: Component {component_name} not found")
            return

        # 使用动画显示
        if self._animation_controller and component.config.enable_animation:
            self._animation_controller.fade_in(
                component, component.config.animation_duration
            )
        else:
            component.show(position)

        # 设置自动隐藏
        if self._config.auto_hide_delay > 0:
            self._setup_auto_hide(component_name)

    def hide_component(self, component_name: str) -> None:
        """隐藏组件"""
        component = self.get_component(component_name)
        if not component:
            return

        # 取消自动隐藏定时器
        if component_name in self._auto_hide_timers:
            self._auto_hide_timers[component_name].stop()
            del self._auto_hide_timers[component_name]

        # 使用动画隐藏
        if self._animation_controller and component.config.enable_animation:
            self._animation_controller.fade_out(
                component, component.config.animation_duration
            )
        else:
            component.hide()

    def update_theme(self, theme_name: str) -> None:
        """更新主题"""
        if not self._theme_manager:
            print("Warning: Theme manager not set")
            return

        try:
            theme = self._theme_manager.load_theme(theme_name)

            # 更新所有组件主题
            for component in self._components.values():
                component.update_theme(theme)

            self._config.theme = theme_name
            self.theme_changed.emit(theme_name)
            print(f"Theme updated to: {theme_name}")

        except Exception as e:
            print(f"Error updating theme: {e}")

    def get_component(self, component_name: str) -> Optional[UIComponent]:
        """获取组件实例"""
        return self._components.get(component_name)

    def list_components(self) -> List[str]:
        """获取所有组件名称"""
        return list(self._components.keys())

    def process_input_event(self, event: UIEvent) -> None:
        """处理输入事件"""
        # 设置时间戳
        event.timestamp = time.time()

        # 添加到事件队列
        self._event_queue.append(event)

        # 发出信号
        self.input_event_received.emit(event)

        # 处理事件
        if not self._is_processing_events:
            self._process_event_queue()

    def set_animation_controller(self, controller: AnimationController) -> None:
        """设置动画控制器"""
        self._animation_controller = controller

    def set_theme_manager(self, manager: ThemeManager) -> None:
        """设置主题管理器"""
        self._theme_manager = manager

    def set_position_manager(self, manager: PositionManager) -> None:
        """设置位置管理器"""
        self._position_manager = manager

    def get_config(self) -> UIConfig:
        """获取UI配置"""
        return self._config

    def update_config(self, config: UIConfig) -> None:
        """更新UI配置"""
        self._config = config

        # 应用配置到所有组件
        for component in self._components.values():
            component.config = config

    def show_all_components(self) -> None:
        """显示所有组件"""
        for component_name in self._components:
            self.show_component(component_name)

    def hide_all_components(self) -> None:
        """隐藏所有组件"""
        for component_name in self._components:
            self.hide_component(component_name)

    def is_main_thread(self) -> bool:
        """检查是否在主线程"""
        return threading.current_thread().ident == self._main_thread_id

    def cleanup(self) -> None:
        """清理资源"""
        # 停止所有定时器
        for timer in self._auto_hide_timers.values():
            timer.stop()
        self._auto_hide_timers.clear()

        # 隐藏所有组件
        self.hide_all_components()

        # 清空组件
        self._components.clear()

    # 私有方法
    def _setup_auto_hide(self, component_name: str) -> None:
        """设置自动隐藏"""
        # 取消现有定时器
        if component_name in self._auto_hide_timers:
            self._auto_hide_timers[component_name].stop()

        # 创建新定时器
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._auto_hide_timeout(component_name))
        timer.start(self._config.auto_hide_delay)

        self._auto_hide_timers[component_name] = timer

    def _auto_hide_timeout(self, component_name: str) -> None:
        """自动隐藏超时处理"""
        self.hide_component(component_name)

    def _process_event_queue(self) -> None:
        """处理事件队列"""
        if self._is_processing_events or not self._event_queue:
            return

        self._is_processing_events = True

        try:
            while self._event_queue:
                event = self._event_queue.pop(0)
                self._handle_input_event(event)

        finally:
            self._is_processing_events = False

    def _handle_input_event(self, event: UIEvent) -> None:
        """处理单个输入事件"""
        event_type = event.event_type

        # 根据事件类型分发到相应组件
        if event_type == "text_input":
            self._handle_text_input(event)
        elif event_type == "candidate_selected":
            self._handle_candidate_selected(event)
        elif event_type == "keyboard_shortcut":
            self._handle_keyboard_shortcut(event)
        elif event_type == "cursor_position_changed":
            self._handle_cursor_position_changed(event)
        else:
            # 广播到其他组件
            for component in self._components.values():
                component._emit_event(event_type, event.data)

    def _handle_text_input(self, event: UIEvent) -> None:
        """处理文本输入事件"""
        text = event.data.get("text", "")

        # 显示候选窗口
        if "candidate" in self._components:
            self.show_component("candidate")

    def _handle_candidate_selected(self, event: UIEvent) -> None:
        """处理候选选择事件"""
        candidate_text = event.data.get("text", "")

        # 隐藏候选窗口
        if "candidate" in self._components:
            self.hide_component("candidate")

    def _handle_keyboard_shortcut(self, event: UIEvent) -> None:
        """处理键盘快捷键事件"""
        shortcut = event.data.get("shortcut", "")

        # 处理全局快捷键
        if shortcut == "toggle_ui":
            self._toggle_ui_visibility()
        elif shortcut == "next_theme":
            self._cycle_theme()

    def _handle_cursor_position_changed(self, event: UIEvent) -> None:
        """处理光标位置变化事件"""
        position = event.data.get("position")
        if not position:
            return

        # 更新跟随光标的组件位置
        for component_name, component in self._components.items():
            if (
                hasattr(component, "config")
                and hasattr(component.config, "follow_cursor")
                and component.config.follow_cursor
            ):
                try:
                    component.move_to_cursor(Position(**position))
                except AttributeError:
                    # 组件没有 move_to_cursor 方法，跳过
                    continue

    def _toggle_ui_visibility(self) -> None:
        """切换UI可见性"""
        visible_components = [
            name
            for name, comp in self._components.items()
            if comp.state == UIState.VISIBLE
        ]

        if visible_components:
            self.hide_all_components()
        else:
            self.show_all_components()

    def _cycle_theme(self) -> None:
        """循环切换主题"""
        if not self._theme_manager:
            return

        themes = self._theme_manager.list_themes()
        if not themes:
            return

        current_index = (
            themes.index(self._config.theme) if self._config.theme in themes else 0
        )
        next_index = (current_index + 1) % len(themes)

        self.update_theme(themes[next_index])

    def _on_component_state_changed(self, event: UIEvent) -> None:
        """组件状态变更处理"""
        data = event.data
        old_state = data.get("old_state")
        new_state = data.get("new_state")

        print(f"Component state changed: {old_state} -> {new_state}")

    def _on_component_position_changed(self, event: UIEvent) -> None:
        """组件位置变更处理"""
        position = event.data.get("position")
        if position and self._position_manager:
            # 验证位置有效性
            if not self._position_manager.is_position_valid(
                Position(**position),
                QSize(400, 300),  # 默认尺寸
            ):
                print("Warning: Component position is invalid")


class SimpleUIManager:
    """简化版UI管理器 - 用于测试"""

    def __init__(self, config: Optional[UIConfig] = None):
        self._components: Dict[str, UIComponent] = {}
        self._config = config or UIConfig()
        self._event_handlers: Dict[str, List[Callable]] = {}

    def register_component(self, component: UIComponent) -> None:
        """注册组件"""
        self._components[component.name] = component

    def show_component(
        self, component_name: str, position: Optional[Position] = None
    ) -> None:
        """显示组件"""
        component = self._components.get(component_name)
        if component:
            component.show(position)

    def hide_component(self, component_name: str) -> None:
        """隐藏组件"""
        component = self._components.get(component_name)
        if component:
            component.hide()

    def get_component(self, component_name: str) -> Optional[UIComponent]:
        """获取组件"""
        return self._components.get(component_name)

    def process_input_event(self, event: UIEvent) -> None:
        """处理输入事件"""
        # 简化版事件处理
        print(f"Processing event: {event.event_type}")

        # 简单的组件状态管理
        if event.event_type == "text_input":
            if "candidate" in self._components:
                self.show_component("candidate")
        elif event.event_type == "candidate_selected":
            if "candidate" in self._components:
                self.hide_component("candidate")
