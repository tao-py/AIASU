from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QObject, Signal, QPoint, QRect, QSize
from PySide6.QtGui import QColor, QFont, QPixmap

# 获取 QObject 的元类
QObjectMeta = type(QObject)

# 创建组合元类
class QObjectABCMeta(QObjectMeta, type(ABC)):
    """组合 QObject 的元类和 ABCMeta，解决多重继承冲突"""
    pass


class UIState(Enum):
    """UI组件状态枚举"""

    HIDDEN = "hidden"
    VISIBLE = "visible"
    ANIMATING = "animating"
    LOADING = "loading"
    ERROR = "error"


@dataclass
class Position:
    """位置信息数据类"""

    x: int
    y: int

    def to_qpoint(self) -> QPoint:
        return QPoint(self.x, self.y)

    @classmethod
    def from_qpoint(cls, point: QPoint) -> "Position":
        return cls(point.x(), point.y())


@dataclass
class UITheme:
    """主题配置数据类"""

    name: str
    background_color: str
    text_color: str
    accent_color: str
    border_color: str
    opacity: float
    border_radius: int
    font_family: str
    font_size: int

    def to_qcolor(self, color_attr: str) -> QColor:
        """将颜色字符串转换为QColor"""
        color_str = getattr(self, color_attr, "#000000")
        return QColor(color_str)


@dataclass
class CandidateItem:
    """候选项目数据类"""

    text: str
    description: str = ""
    icon: Optional[QPixmap] = None
    score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UIConfig:
    """UI配置数据类"""

    theme: str = "default"
    opacity: float = 0.95
    animation_duration: int = 200
    max_candidates: int = 5
    window_padding: int = 8
    font_size: int = 14
    follow_cursor: bool = True
    multi_monitor: bool = True
    auto_hide_delay: int = 3000
    enable_animation: bool = True


class UIEvent:
    """UI事件基类"""

    def __init__(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        self.event_type = event_type
        self.data = data or {}
        self.timestamp: float = 0.0  # 将在实际使用时设置


class UIComponent(ABC):
    """UI组件抽象基类"""

    def __init__(self, name: str, config: Optional[UIConfig] = None):
        self.name = name
        self.config = config or UIConfig()
        self.state = UIState.HIDDEN
        self._signals = {}
        self._event_handlers: Dict[str, List[Callable]] = {}

    @abstractmethod
    def show(self, position: Optional[Position] = None) -> None:
        """显示组件"""
        pass

    @abstractmethod
    def hide(self) -> None:
        """隐藏组件"""
        pass

    @abstractmethod
    def update_theme(self, theme: UITheme) -> None:
        """更新主题"""
        pass

    @abstractmethod
    def get_preferred_size(self) -> QSize:
        """获取组件推荐尺寸"""
        pass

    def set_state(self, state: UIState) -> None:
        """设置组件状态"""
        old_state = self.state
        self.state = state
        self._emit_event("state_changed", {"old_state": old_state, "new_state": state})

    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """添加事件处理器"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)

    def remove_event_handler(self, event_type: str, handler: Callable) -> None:
        """移除事件处理器"""
        if event_type in self._event_handlers:
            self._event_handlers[event_type].remove(handler)

    def _emit_event(
        self, event_type: str, data: Optional[Dict[str, Any]] = None
    ) -> None:
        """触发事件"""
        event = UIEvent(event_type, data)
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler for {event_type}: {e}")


class WindowComponent(UIComponent):
    """窗口组件抽象类"""

    def __init__(self, name: str, config: Optional[UIConfig] = None):
        super().__init__(name, config)
        self._window = None
        self._position = Position(0, 0)
        self._size = QSize(400, 300)

    @abstractmethod
    def create_window(self) -> None:
        """创建窗口"""
        pass

    @abstractmethod
    def set_position(self, position: Position) -> None:
        """设置窗口位置"""
        pass

    @abstractmethod
    def set_content(self, content: Any) -> None:
        """设置窗口内容"""
        pass

    def move_to_cursor(self, cursor_pos: Position) -> None:
        """移动到光标位置"""
        if self.config.follow_cursor:
            self.set_position(cursor_pos)

    def get_window_rect(self) -> Any:
        """获取窗口矩形"""
        return QRect()


class AnimationController(ABC):
    """动画控制器抽象类"""

    @abstractmethod
    def fade_in(self, component: UIComponent, duration: int = 200) -> None:
        """淡入动画"""
        pass

    @abstractmethod
    def fade_out(self, component: UIComponent, duration: int = 200) -> None:
        """淡出动画"""
        pass

    @abstractmethod
    def slide_in(
        self, component: UIComponent, direction: str = "bottom", duration: int = 200
    ) -> None:
        """滑入动画"""
        pass

    @abstractmethod
    def slide_out(
        self, component: UIComponent, direction: str = "bottom", duration: int = 200
    ) -> None:
        """滑出动画"""
        pass

    @abstractmethod
    def scale_in(self, component: UIComponent, duration: int = 200) -> None:
        """缩放进入动画"""
        pass


class ThemeManager(ABC):
    """主题管理器抽象类"""

    @abstractmethod
    def load_theme(self, theme_name: str) -> UITheme:
        """加载主题"""
        pass

    @abstractmethod
    def save_theme(self, theme: UITheme) -> None:
        """保存主题"""
        pass

    @abstractmethod
    def list_themes(self) -> List[str]:
        """获取可用主题列表"""
        pass

    @abstractmethod
    def get_current_theme(self) -> UITheme:
        """获取当前主题"""
        pass


class PositionManager(ABC):
    """位置管理器抽象类"""

    @abstractmethod
    def calculate_optimal_position(
        self, window_size: QSize, cursor_pos: Position, screen_rect: QRect
    ) -> Position:
        """计算最佳窗口位置"""
        pass

    @abstractmethod
    def get_screen_info(self) -> Dict[str, Any]:
        """获取屏幕信息"""
        pass

    @abstractmethod
    def is_position_valid(self, position: Position, window_size: QSize) -> bool:
        """检查位置是否有效"""
        pass


class UIManagerInterface(ABC):
    """UI管理器接口"""
    # 注意：这里不指定元类，将在需要时使用 QObjectABCMeta

    @abstractmethod
    def register_component(self, component: UIComponent) -> None:
        """注册UI组件"""
        pass

    @abstractmethod
    def unregister_component(self, component_name: str) -> None:
        """注销UI组件"""
        pass

    @abstractmethod
    def show_component(
        self, component_name: str, position: Optional[Position] = None
    ) -> None:
        """显示组件"""
        pass

    @abstractmethod
    def hide_component(self, component_name: str) -> None:
        """隐藏组件"""
        pass

    @abstractmethod
    def update_theme(self, theme_name: str) -> None:
        """更新主题"""
        pass

    @abstractmethod
    def get_component(self, component_name: str) -> Optional[UIComponent]:
        """获取组件实例"""
        pass

    @abstractmethod
    def process_input_event(self, event: UIEvent) -> None:
        """处理输入事件"""
        pass


class MenuBarInterface(ABC):
    """菜单栏接口"""

    @abstractmethod
    def create_menu(self, config: Dict[str, Any]) -> None:
        """创建菜单"""
        pass

    @abstractmethod
    def update_menu_item(
        self, item_id: str, enabled: bool = True, checked: bool = False
    ) -> None:
        """更新菜单项"""
        pass

    @abstractmethod
    def show_notification(self, title: str, message: str, duration: int = 3000) -> None:
        """显示通知"""
        pass

    @abstractmethod
    def quit(self) -> None:
        """退出应用"""
        pass
    