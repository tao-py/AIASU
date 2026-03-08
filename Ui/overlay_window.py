from typing import Optional, Dict, Any
from PySide6.QtCore import (
    Qt,
    QPoint,
    QRect,
    QPropertyAnimation,
    QEasingCurve,
    QTimer,
    QSize,
)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QPainterPath, QRegion

from .base import WindowComponent, Position, UITheme, UIConfig, UIState


class OverlayWindow(WindowComponent):
    """悬浮窗口组件 - 支持透明背景、阴影、圆角等效果"""

    def __init__(self, name: str = "overlay", config: Optional[UIConfig] = None):
        super().__init__(name, config)
        self._window = None
        self._content_widget = None
        self._background_opacity = 0.95
        self._border_radius = 12
        self._shadow_enabled = True
        self._shadow_blur_radius = 20
        self._shadow_offset = QPoint(0, 4)
        self._current_theme: Optional[UITheme] = None
        self._animations: Dict[str, QPropertyAnimation] = {}
        self._auto_hide_timer: Optional[QTimer] = None
        self._drag_enabled = False
        self._drag_start_pos = QPoint()

        self._init_window()

    def _init_window(self):
        """初始化窗口"""
        self._window = OverlayWindowWidget(self)
        self._window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self._window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._window.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._window.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)

        # 设置窗口透明度
        self._window.setWindowOpacity(self._background_opacity)

        # 初始化内容区域
        self._init_content_area()

        # 设置默认大小
        self._window.resize(400, 200)

    def _init_content_area(self):
        """初始化内容区域"""
        self._content_widget = QWidget(self._window)
        self._content_widget.setObjectName("content_area")

        # 创建布局
        layout = QVBoxLayout(self._content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 添加占位标签
        placeholder = QLabel("Overlay Window Content")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setObjectName("placeholder_label")
        layout.addWidget(placeholder)

        # 设置内容区域样式
        self._update_content_style()

    def show(self, position: Optional[Position] = None) -> None:
        """显示窗口"""
        if not self._window:
            return

        self.set_state(UIState.VISIBLE)

        # 设置位置
        if position:
            self.set_position(position)

        # 显示窗口
        self._window.show()

        # 播放显示动画
        self._play_show_animation()

        print(f"Overlay window shown at position: {self._position}")

    def hide(self) -> None:
        """隐藏窗口"""
        if not self._window:
            return

        self.set_state(UIState.HIDDEN)

        # 播放隐藏动画
        self._play_hide_animation()

        print("Overlay window hidden")

    def update_theme(self, theme: UITheme) -> None:
        """更新主题"""
        self._current_theme = theme

        # 更新背景透明度
        self._background_opacity = theme.opacity
        if self._window:
            self._window.setWindowOpacity(self._background_opacity)

        # 更新内容区域样式
        self._update_content_style()

        # 更新阴影效果
        self._update_shadow_effect()

        print(f"Overlay theme updated: {theme.name}")

    def set_position(self, position: Position) -> None:
        """设置窗口位置"""
        self._position = position
        if self._window:
            self._window.move(position.x, position.y)

    def set_content(self, content: Any) -> None:
        """设置窗口内容"""
        if not self._content_widget:
            return

        # 清除现有内容
        layout = self._content_widget.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # 添加新内容
        if hasattr(content, "widget"):
            layout.addWidget(content.widget())
        elif hasattr(content, "show"):
            layout.addWidget(content)
        else:
            # 默认处理 - 创建标签显示内容
            label = QLabel(str(content))
            label.setWordWrap(True)
            label.setObjectName("content_label")
            layout.addWidget(label)

    def get_preferred_size(self) -> QSize:
        """获取推荐尺寸"""
        if self._content_widget:
            return self._content_widget.sizeHint() + QSize(40, 40)  # 添加边距
        return QSize(400, 200)

    def set_opacity(self, opacity: float) -> None:
        """设置透明度"""
        self._background_opacity = max(0.1, min(1.0, opacity))
        if self._window:
            self._window.setWindowOpacity(self._background_opacity)

    def set_border_radius(self, radius: int) -> None:
        """设置圆角半径"""
        self._border_radius = max(0, radius)
        self._update_content_style()

    def enable_shadow(self, enabled: bool) -> None:
        """启用/禁用阴影效果"""
        self._shadow_enabled = enabled
        self._update_shadow_effect()

    def enable_drag(self, enabled: bool) -> None:
        """启用/禁用拖拽"""
        self._drag_enabled = enabled

    def set_auto_hide_delay(self, delay_ms: int) -> None:
        """设置自动隐藏延迟"""
        if delay_ms <= 0:
            if self._auto_hide_timer:
                self._auto_hide_timer.stop()
                self._auto_hide_timer = None
            return

        if not self._auto_hide_timer:
            self._auto_hide_timer = QTimer()
            self._auto_hide_timer.setSingleShot(True)
            self._auto_hide_timer.timeout.connect(self.hide)

        self._auto_hide_timer.setInterval(delay_ms)

    def reset_auto_hide_timer(self) -> None:
        """重置自动隐藏定时器"""
        if self._auto_hide_timer and self._auto_hide_timer.isActive():
            self._auto_hide_timer.stop()
            self._auto_hide_timer.start()

    def fade_in(self, duration: int = 200) -> None:
        """淡入动画"""
        if not self._window:
            return

        self.set_state(UIState.ANIMATING)

        # 创建透明度动画
        animation = QPropertyAnimation(self._window, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(self._background_opacity)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 连接完成信号
        animation.finished.connect(lambda: self.set_state(UIState.VISIBLE))

        # 开始动画
        animation.start()
        self._animations["fade_in"] = animation

    def fade_out(self, duration: int = 200) -> None:
        """淡出动画"""
        if not self._window:
            return

        self.set_state(UIState.ANIMATING)

        # 创建透明度动画
        animation = QPropertyAnimation(self._window, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(self._background_opacity)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.Type.InCubic)

        # 连接完成信号
        animation.finished.connect(lambda: self._on_fade_out_complete())

        # 开始动画
        animation.start()
        self._animations["fade_out"] = animation

    def _play_show_animation(self) -> None:
        """播放显示动画"""
        if self.config.enable_animation:
            self.fade_in(self.config.animation_duration)

    def _play_hide_animation(self) -> None:
        """播放隐藏动画"""
        if self.config.enable_animation:
            self.fade_out(self.config.animation_duration)
        else:
            self._on_hide_complete()

    def _on_fade_out_complete(self) -> None:
        """淡出动画完成处理"""
        if self._window:
            self._window.hide()
        self.set_state(UIState.HIDDEN)

    def _on_hide_complete(self) -> None:
        """隐藏完成处理"""
        if self._window:
            self._window.hide()

    def _update_content_style(self) -> None:
        """更新内容区域样式"""
        if not self._content_widget or not self._current_theme:
            return

        style_sheet = f"""
        QWidget#content_area {{
            background-color: {self._current_theme.background_color};
            border-radius: {self._border_radius}px;
            border: 1px solid {self._current_theme.border_color};
        }}
        
        QLabel {{
            color: {self._current_theme.text_color};
            font-family: {self._current_theme.font_family};
            font-size: {self._current_theme.font_size}px;
            background: transparent;
        }}
        
        QLabel#placeholder_label {{
            color: {self._current_theme.text_color};
            opacity: 0.6;
        }}
        """

        self._content_widget.setStyleSheet(style_sheet)

    def _update_shadow_effect(self) -> None:
        """更新阴影效果"""
        if not self._window:
            return

        if self._shadow_enabled and self._current_theme:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(self._shadow_blur_radius)
            shadow.setColor(QColor(self._current_theme.border_color))
            shadow.setOffset(self._shadow_offset)
            self._window.setGraphicsEffect(shadow)
        else:
            # 使用空的效果对象来清除阴影
            self._window.setGraphicsEffect(QGraphicsDropShadowEffect())

    def is_visible(self) -> bool:
        """检查窗口是否可见"""
        return bool(self._window and self._window.isVisible())

    def get_window_rect(self) -> QRect:
        """获取窗口矩形"""
        if self._window:
            return self._window.geometry()
        return QRect()

    def move_to_cursor(self, cursor_pos: Position) -> None:
        """移动到光标位置"""
        super().move_to_cursor(cursor_pos)

        # 添加偏移量，避免遮挡光标
        offset_pos = Position(cursor_pos.x, cursor_pos.y + 20)
        self.set_position(offset_pos)


class OverlayWindowWidget(QWidget):
    """悬浮窗口部件 - 自定义绘制和事件处理"""

    def __init__(self, overlay_component: OverlayWindow):
        super().__init__()
        self._overlay = overlay_component
        self._mouse_pressed = False
        self._drag_start_pos: Optional[QPoint] = None

    def paintEvent(self, event):
        """自定义绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 获取窗口矩形
        rect = self.rect()

        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(
            rect, self._overlay._border_radius, self._overlay._border_radius
        )

        # 设置绘制区域
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

        # 背景透明，内容由样式表控制
        painter.fillPath(path, QBrush(QColor(0, 0, 0, 0)))

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton and self._overlay._drag_enabled:
            self._mouse_pressed = True
            self._drag_start_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self._mouse_pressed and self._overlay._drag_enabled and self._drag_start_pos:
            new_pos = event.globalPosition().toPoint() - self._drag_start_pos
            self.move(new_pos)

            # 更新位置信息
            self._overlay._position = Position(new_pos.x(), new_pos.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_pressed = False
            self._drag_start_pos = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """鼠标进入事件"""
        # 重置自动隐藏定时器
        if self._overlay._auto_hide_timer:
            self._overlay.reset_auto_hide_timer()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
