from typing import Optional, Dict, Any
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve, QObject
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFrame,
    QScrollArea,
    QGridLayout,
)
from PySide6.QtGui import (
    QFont,
    QPainter,
    QColor,
    QBrush,
    QPen,
    QTextCharFormat,
    QTextCursor,
)

from .base import UIComponent, Position, UITheme, UIConfig, UIState, QObjectABCMeta


class InputPreview(UIComponent, QObject, metaclass=QObjectABCMeta):
    """输入预览组件 - 显示输入内容和候选预览"""

    # 自定义信号
    text_changed = Signal(str)  # 文本变更
    preview_requested = Signal(str)  # 预览请求
    selection_changed = Signal(int)  # 选择变更

    def __init__(self, name: str = "input_preview", config: Optional[UIConfig] = None):
        super().__init__(name, config)
        self._widget = None
        self._text_edit = None
        self._preview_label = None
        self._status_label = None
        self._current_text = ""
        self._preview_text = ""
        self._cursor_position = 0
        self._selection_start = 0
        self._selection_end = 0
        self._max_length = 1000
        self._show_line_numbers = False
        self._show_status_bar = True
        self._current_theme: Optional[UITheme] = None
        self._animations: Dict[str, QPropertyAnimation] = {}

        self._init_widget()

    def _init_widget(self):
        """初始化组件"""
        self._widget = QWidget()
        self._widget.setObjectName("input_preview")
        self._widget.setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
        )
        self._widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 创建主布局
        main_layout = QVBoxLayout(self._widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建文本编辑区域
        self._create_text_edit()
        main_layout.addWidget(self._text_edit)

        # 创建状态栏
        self._create_status_bar()
        if self._status_label:
            main_layout.addWidget(self._status_label)

        # 设置样式
        self._update_style()

        # 设置默认大小
        self._widget.resize(500, 150)

    def _create_text_edit(self):
        """创建文本编辑区域"""
        self._text_edit = QTextEdit()
        self._text_edit.setObjectName("preview_text_edit")
        self._text_edit.setReadOnly(True)
        self._text_edit.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._text_edit.setMaximumHeight(100)
        self._text_edit.setPlaceholderText("输入预览将显示在这里...")
        self._text_edit.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # 连接信号
        self._text_edit.textChanged.connect(self._on_text_changed)
        self._text_edit.cursorPositionChanged.connect(self._on_cursor_position_changed)

    def _create_status_bar(self):
        """创建状态栏"""
        if not self._show_status_bar:
            return

        self._status_label = QLabel("就绪")
        self._status_label.setObjectName("status_label")
        self._status_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self._status_label.setFixedHeight(20)

    def show(self, position: Optional[Position] = None) -> None:
        """显示输入预览"""
        if not self._widget:
            return

        self.set_state(UIState.VISIBLE)

        # 设置位置
        if position:
            self._widget.move(position.x, position.y)

        # 显示组件
        self._widget.show()

        # 播放显示动画
        self._play_show_animation()

        print(f"Input preview shown with text: '{self._current_text}'")

    def hide(self) -> None:
        """隐藏输入预览"""
        if not self._widget:
            return

        self.set_state(UIState.HIDDEN)

        # 播放隐藏动画
        self._play_hide_animation()

        print("Input preview hidden")

    def update_theme(self, theme: UITheme) -> None:
        """更新主题"""
        self._current_theme = theme
        self._update_style()
        print(f"Input preview theme updated: {theme.name}")

    def set_text(self, text: str) -> None:
        """设置预览文本"""
        if len(text) > self._max_length:
            text = text[: self._max_length] + "..."

        self._current_text = text

        if self._text_edit:
            self._text_edit.setPlainText(text)

        # 发出信号
        self.text_changed.emit(text)

        # 更新状态栏
        self._update_status()

        # 如果没有文本，自动隐藏
        if not text.strip():
            self.hide()
        elif not self.is_visible():
            self.show()

    def set_preview_text(self, text: str) -> None:
        """设置候选预览文本"""
        self._preview_text = text

        if self._preview_label:
            self._preview_label.setText(text)

        # 发出预览请求信号
        self.preview_requested.emit(text)

    def append_text(self, text: str) -> None:
        """追加文本"""
        new_text = self._current_text + text
        self.set_text(new_text)

    def insert_text(self, text: str, position: int = -1) -> None:
        """在指定位置插入文本"""
        if position < 0:
            position = len(self._current_text)

        new_text = self._current_text[:position] + text + self._current_text[position:]
        self.set_text(new_text)

    def clear_text(self) -> None:
        """清空文本"""
        self.set_text("")

    def highlight_text(self, start: int, end: int, color: str = "#007AFF") -> None:
        """高亮文本"""
        if not self._text_edit:
            return

        cursor = QTextCursor(self._text_edit.document())
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)

        # 设置高亮格式
        format = QTextCharFormat()
        format.setBackground(QColor(color))
        cursor.setCharFormat(format)

    def set_cursor_position(self, position: int) -> None:
        """设置光标位置"""
        if not self._text_edit or position < 0 or position > len(self._current_text):
            return

        self._cursor_position = position

        cursor = self._text_edit.textCursor()
        cursor.setPosition(position)
        self._text_edit.setTextCursor(cursor)

    def get_preferred_size(self) -> QSize:
        """获取推荐尺寸"""
        width = 500
        height = 100  # 基础高度

        # 计算文本高度
        if self._text_edit:
            text_height = self._text_edit.document().size().height() + 20
            height = max(height, text_height)

        # 添加状态栏高度
        if self._status_label and self._show_status_bar:
            height += 20

        # 添加边距
        height += 20

        return QSize(width, min(height, 300))  # 最大高度300

    def enable_line_numbers(self, enabled: bool) -> None:
        """启用/禁用时显示行号"""
        self._show_line_numbers = enabled
        # TODO: 实现行号显示

    def enable_status_bar(self, enabled: bool) -> None:
        """启用/禁用状态栏"""
        self._show_status_bar = enabled
        if self._status_label:
            self._status_label.setVisible(enabled)

    def set_max_length(self, length: int) -> None:
        """设置最大文本长度"""
        self._max_length = max(1, length)

    def move_to_cursor(self, cursor_pos: Position) -> None:
        """移动到光标位置"""
        if self.config.follow_cursor:
            # 添加偏移量，避免遮挡光标
            offset_pos = Position(cursor_pos.x, cursor_pos.y + 20)
            if self._widget:
                self._widget.move(offset_pos.x, offset_pos.y)

    def is_visible(self) -> bool:
        """检查是否可见"""
        return self._widget and self._widget.isVisible()

    def _update_style(self) -> None:
        """更新样式"""
        if not self._widget or not self._current_theme:
            return

        style_sheet = f"""
        QWidget#input_preview {{
            background-color: {self._current_theme.background_color};
            border: 1px solid {self._current_theme.border_color};
            border-radius: 8px;
        }}
        
        QTextEdit#preview_text_edit {{
            background: transparent;
            border: none;
            color: {self._current_theme.text_color};
            font-family: {self._current_theme.font_family};
            font-size: {self._current_theme.font_size}px;
            padding: 8px;
        }}
        
        QTextEdit#preview_text_edit:focus {{
            border: none;
        }}
        
        QLabel#status_label {{
            background-color: rgba(0, 0, 0, 20);
            color: {self._current_theme.text_color};
            font-size: 10px;
            padding: 2px 8px;
        }}
        """

        self._widget.setStyleSheet(style_sheet)

    def _update_status(self) -> None:
        """更新状态栏"""
        if not self._status_label:
            return

        text_length = len(self._current_text)
        status_text = f"长度: {text_length}"

        if self._preview_text:
            status_text += f" | 预览: {self._preview_text}"

        self._status_label.setText(status_text)

    def _play_show_animation(self) -> None:
        """播放显示动画"""
        if self.config.enable_animation and self._widget:
            # 淡入动画
            animation = QPropertyAnimation(self._widget, b"windowOpacity")
            animation.setDuration(self.config.animation_duration)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.start()
            self._animations["fade_in"] = animation

    def _play_hide_animation(self) -> None:
        """播放隐藏动画"""
        if self.config.enable_animation and self._widget:
            # 淡出动画
            animation = QPropertyAnimation(self._widget, b"windowOpacity")
            animation.setDuration(self.config.animation_duration)
            animation.setStartValue(1.0)
            animation.setEndValue(0.0)
            animation.finished.connect(self._widget.hide)
            animation.start()
            self._animations["fade_out"] = animation
        else:
            if self._widget:
                self._widget.hide()

    def _on_text_changed(self) -> None:
        """文本变更事件"""
        if self._text_edit:
            self._current_text = self._text_edit.toPlainText()
            self.text_changed.emit(self._current_text)
            self._update_status()

    def _on_cursor_position_changed(self) -> None:
        """光标位置变更事件"""
        if self._text_edit:
            cursor = self._text_edit.textCursor()
            self._cursor_position = cursor.position()
            self.selection_changed.emit(self._cursor_position)


class SimpleInputPreview:
    """简化版输入预览 - 用于测试"""

    def __init__(self):
        self.current_text = ""
        self.preview_text = ""
        self.is_visible = False

    def set_text(self, text: str) -> None:
        """设置预览文本"""
        self.current_text = text
        print(f"Preview text: '{text}'")

        if text.strip():
            self.is_visible = True
        else:
            self.is_visible = False

    def set_preview_text(self, text: str) -> None:
        """设置候选预览文本"""
        self.preview_text = text
        print(f"Candidate preview: '{text}'")

    def append_text(self, text: str) -> None:
        """追加文本"""
        self.current_text += text
        print(f"Appended text: '{text}'")

    def clear_text(self) -> None:
        """清空文本"""
        self.current_text = ""
        self.preview_text = ""
        self.is_visible = False
        print("Preview cleared")
