from typing import Optional, List, Dict, Any
from PySide6.QtCore import (
    Qt,
    QTimer,
    QPoint,
    Signal,
    QSize,
    QPropertyAnimation,
    QEasingCurve,
    QObject,
)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PySide6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QPainterPath, QRegion

from .base import WindowComponent, Position, UITheme, UIConfig, UIState, CandidateItem,QObjectABCMeta
from .candidate_view import CandidateView


class IMEWindow(QObject, WindowComponent, metaclass=QObjectABCMeta):
    """输入法窗口 - 整合候选列表和输入预览"""

    # 自定义信号
    composition_changed = Signal(str)  # 输入内容变更
    candidate_selected = Signal(str)  # 候选被选中
    ime_hidden = Signal()  # IME隐藏

    def __init__(self, name: str = "ime", config: Optional[UIConfig] = None):
        QObject.__init__(self)
        WindowComponent.__init__(self, name, config)
        self._window = None
        self._candidate_view = None
        self._preview_widget = None
        self._composition_text = ""
        self._cursor_position = Position(0, 0)
        self._follow_cursor_timer = None
        self._auto_hide_timer = None
        self._current_theme: Optional[UITheme] = None
        self._animations: Dict[str, QPropertyAnimation] = {}
        self._show_preview = True
        self._show_candidates = True
        self._follow_cursor_enabled = True
        self._cursor_offset = QPoint(10, 25)

        self._init_window()

    def _init_window(self):
        """初始化窗口"""
        self._window = QWidget()
        self._window.setObjectName("ime_window")
        self._window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self._window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._window.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._window.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # 初始化组件
        self._init_candidate_view()
        self._init_preview_widget()
        self._init_layout()
        self._init_timers()

        # 设置默认大小
        self._window.resize(400, 300)

    def _init_candidate_view(self):
        """初始化候选视图"""
        self._candidate_view = CandidateView("ime_candidate", self.config)
        self._candidate_view.candidate_selected.connect(self._on_candidate_selected)
        self._candidate_view.add_event_handler(
            "state_changed", self._on_candidate_state_changed
        )

    def _init_preview_widget(self):
        """初始化预览部件"""
        self._preview_widget = QTextEdit(self._window)
        self._preview_widget.setObjectName("preview_widget")
        self._preview_widget.setReadOnly(True)
        self._preview_widget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._preview_widget.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._preview_widget.setMaximumHeight(60)
        self._preview_widget.setPlaceholderText("输入预览...")
        self._preview_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def _init_layout(self):
        """初始化布局"""
        if not self._window:
            return

        layout = QVBoxLayout(self._window)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # 添加预览部件
        if self._show_preview and self._preview_widget:
            layout.addWidget(self._preview_widget)

        # 添加候选视图
        if (
            self._show_candidates
            and self._candidate_view
            and hasattr(self._candidate_view, "_widget")
            and self._candidate_view._widget
        ):
            layout.addWidget(self._candidate_view._widget)

        # 设置样式
        self._update_style()

    def _init_timers(self):
        """初始化定时器"""
        # 光标跟随定时器
        self._follow_cursor_timer = QTimer()
        self._follow_cursor_timer.setInterval(16)  # 60 FPS
        self._follow_cursor_timer.timeout.connect(self._follow_cursor)

        # 自动隐藏定时器
        self._auto_hide_timer = QTimer()
        self._auto_hide_timer.setSingleShot(True)
        self._auto_hide_timer.timeout.connect(self.hide)

    def show(self, position: Optional[Position] = None) -> None:
        """显示IME窗口"""
        if not self._window:
            return

        self.set_state(UIState.VISIBLE)

        # 设置位置
        if position:
            self.set_position(position)

        # 显示窗口
        self._window.show()

        # 启动光标跟随
        if (
            self._follow_cursor_enabled
            and self._follow_cursor_timer
            and hasattr(self._follow_cursor_timer, "start")
        ):
            self._follow_cursor_timer.start()

        # 启动自动隐藏
        self._start_auto_hide_timer()

        # 播放显示动画
        self._play_show_animation()

        print(f"IME window shown at position: {self._position}")

    def hide(self) -> None:
        """隐藏IME窗口"""
        if not self._window:
            return

        self.set_state(UIState.HIDDEN)

        # 停止光标跟随
        if self._follow_cursor_timer:
            self._follow_cursor_timer.stop()

        # 停止自动隐藏
        if self._auto_hide_timer:
            self._auto_hide_timer.stop()

        # 播放隐藏动画
        self._play_hide_animation()

        # 发出隐藏信号
        self.ime_hidden.emit()

        print("IME window hidden")

    def update_theme(self, theme: UITheme) -> None:
        """更新主题"""
        self._current_theme = theme

        # 更新候选视图主题
        if self._candidate_view:
            self._candidate_view.update_theme(theme)

        # 更新窗口样式
        self._update_style()

        print(f"IME theme updated: {theme.name}")

    def set_position(self, position: Position) -> None:
        """设置窗口位置"""
        self._position = position
        if self._window:
            self._window.move(position.x, position.y)

    def set_composition_text(self, text: str) -> None:
        """设置输入组合文本"""
        self._composition_text = text

        # 更新预览部件
        if self._preview_widget:
            self._preview_widget.setPlainText(text)

        # 发出信号
        self.composition_changed.emit(text)

        # 重置自动隐藏定时器
        self._reset_auto_hide_timer()

        # 如果没有文本，自动隐藏
        if not text.strip():
            self.hide()
        elif not self.is_visible():
            self.show()

    def set_candidates(self, candidates: List[CandidateItem]) -> None:
        """设置候选列表"""
        if self._candidate_view:
            self._candidate_view.set_candidates(candidates)

        # 如果没有候选，隐藏候选视图
        if (
            not candidates
            and self._candidate_view
            and hasattr(self._candidate_view, "_widget")
        ):
            self._candidate_view.hide()

        # 重置自动隐藏定时器
        self._reset_auto_hide_timer()

    def select_next_candidate(self) -> None:
        """选择下一个候选"""
        if self._candidate_view:
            self._candidate_view.select_next()

    def select_previous_candidate(self) -> None:
        """选择上一个候选"""
        if self._candidate_view:
            self._candidate_view.select_previous()

    def confirm_selection(self) -> Optional[str]:
        """确认当前选择"""
        if self._candidate_view:
            candidate = self._candidate_view.get_selected_candidate()
            if candidate:
                self.candidate_selected.emit(candidate.text)
                return candidate.text
        return None

    def get_preferred_size(self) -> QSize:
        """获取推荐尺寸"""
        width = 400
        height = 100  # 基础高度

        # 计算预览区域高度
        if self._show_preview and self._preview_widget:
            height += 60

        # 计算候选区域高度
        if self._show_candidates and self._candidate_view:
            candidate_height = self._candidate_view.get_preferred_size().height()
            height += candidate_height

        return QSize(width, height)

    def enable_preview(self, enabled: bool) -> None:
        """启用/禁用输入预览"""
        self._show_preview = enabled
        if self._preview_widget and hasattr(self._preview_widget, "setVisible"):
            self._preview_widget.setVisible(enabled)

    def enable_candidates(self, enabled: bool) -> None:
        """启用/禁用候选显示"""
        self._show_candidates = enabled
        if (
            self._candidate_view
            and hasattr(self._candidate_view, "_widget")
            and self._candidate_view._widget
            and hasattr(self._candidate_view._widget, "setVisible")
        ):
            self._candidate_view._widget.setVisible(enabled)

    def enable_follow_cursor(self, enabled: bool) -> None:
        """启用/禁用光标跟随"""
        self._follow_cursor_enabled = enabled

        if enabled:
            if (
                self._follow_cursor_timer
                and self.is_visible()
                and hasattr(self._follow_cursor_timer, "start")
            ):
                self._follow_cursor_timer.start()
        else:
            if self._follow_cursor_timer and hasattr(self._follow_cursor_timer, "stop"):
                self._follow_cursor_timer.stop()

    def set_cursor_offset(self, offset: QPoint) -> None:
        """设置光标偏移"""
        self._cursor_offset = offset

    def move_to_cursor(self, cursor_pos: Position) -> None:
        """移动到光标位置"""
        if self.config.follow_cursor:
            # 添加偏移量
            offset_pos = Position(
                cursor_pos.x + self._cursor_offset.x(),
                cursor_pos.y + self._cursor_offset.y(),
            )
            self.set_position(offset_pos)

    def is_visible(self) -> bool:
        """检查窗口是否可见"""
        return bool(self._window and self._window.isVisible())

    def _follow_cursor(self) -> None:
        """跟随光标"""
        # 这里应该调用平台相关的光标位置获取
        # 暂时使用模拟位置
        new_pos = Position(self._cursor_position.x + 1, self._cursor_position.y)
        if new_pos != self._cursor_position:
            self._cursor_position = new_pos
            self.move_to_cursor(new_pos)

    def _on_candidate_selected(self, text: str) -> None:
        """候选选择事件"""
        self.candidate_selected.emit(text)
        # 选择后自动隐藏
        self.hide()

    def _on_candidate_state_changed(self, event) -> None:
        """候选视图状态变更事件"""
        # 处理候选视图状态变更
        pass

    def _start_auto_hide_timer(self) -> None:
        """启动自动隐藏定时器"""
        if self._auto_hide_timer and self.config.auto_hide_delay > 0:
            self._auto_hide_timer.start(self.config.auto_hide_delay)

    def _reset_auto_hide_timer(self) -> None:
        """重置自动隐藏定时器"""
        if self._auto_hide_timer and self.config.auto_hide_delay > 0:
            self._auto_hide_timer.stop()
            self._auto_hide_timer.start(self.config.auto_hide_delay)

    def _play_show_animation(self) -> None:
        """播放显示动画"""
        if self.config.enable_animation and self._window:
            # 淡入动画
            animation = QPropertyAnimation(self._window, b"windowOpacity")
            animation.setDuration(self.config.animation_duration)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.start()
            self._animations["fade_in"] = animation

    def _play_hide_animation(self) -> None:
        """播放隐藏动画"""
        if self.config.enable_animation and self._window:
            # 淡出动画
            animation = QPropertyAnimation(self._window, b"windowOpacity")
            animation.setDuration(self.config.animation_duration)
            animation.setStartValue(1.0)
            animation.setEndValue(0.0)
            animation.setEasingCurve(QEasingCurve.Type.InCubic)
            animation.finished.connect(self._on_hide_complete)
            animation.start()
            self._animations["fade_out"] = animation
        else:
            self._on_hide_complete()

    def _on_hide_complete(self) -> None:
        """隐藏完成处理"""
        if self._window:
            self._window.hide()

    def _update_style(self) -> None:
        """更新样式"""
        if not self._window or not self._current_theme:
            return

        style_sheet = f"""
        QWidget#ime_window {{
            background-color: {self._current_theme.background_color};
            border: 1px solid {self._current_theme.border_color};
            border-radius: 8px;
        }}
        
        QTextEdit#preview_widget {{
            background: transparent;
            border: 1px solid {self._current_theme.border_color};
            border-radius: 4px;
            color: {self._current_theme.text_color};
            font-family: {self._current_theme.font_family};
            font-size: {self._current_theme.font_size}px;
            padding: 8px;
        }}
        
        QTextEdit#preview_widget:focus {{
            border: 1px solid {self._current_theme.accent_color};
        }}
        """

        self._window.setStyleSheet(style_sheet)

    def cleanup(self) -> None:
        """清理资源"""
        if self._follow_cursor_timer:
            self._follow_cursor_timer.stop()

        if self._auto_hide_timer:
            self._auto_hide_timer.stop()

        if self._window:
            self._window.hide()


class SimpleIMEWindow:
    """简化版IME窗口 - 用于测试"""

    def __init__(self):
        self.composition_text = ""
        self.candidates: List[CandidateItem] = []
        self.selected_index = -1
        self.is_visible = False

    def set_composition_text(self, text: str) -> None:
        """设置输入组合文本"""
        self.composition_text = text
        print(f"Composition: {text}")

        if text.strip():
            self.is_visible = True
        else:
            self.is_visible = False

    def set_candidates(self, candidates: List[CandidateItem]) -> None:
        """设置候选列表"""
        self.candidates = candidates
        print(f"Candidates: {[c.text for c in candidates]}")

    def select_next_candidate(self) -> None:
        """选择下一个候选"""
        if self.candidates:
            self.selected_index = (self.selected_index + 1) % len(self.candidates)
            print(f"Selected: {self.candidates[self.selected_index].text}")

    def select_previous_candidate(self) -> None:
        """选择上一个候选"""
        if self.candidates:
            self.selected_index = (self.selected_index - 1) % len(self.candidates)
            print(f"Selected: {self.candidates[self.selected_index].text}")

    def confirm_selection(self) -> Optional[str]:
        """确认当前选择"""
        if 0 <= self.selected_index < len(self.candidates):
            selected = self.candidates[self.selected_index].text
            print(f"Confirmed: {selected}")
            self.is_visible = False
            return selected
        return None
