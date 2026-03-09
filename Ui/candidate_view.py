from typing import Optional, List, Dict, Any, Callable
from PySide6.QtCore import (
    Qt,
    Signal,
    QSize,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
    QObject,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QFrame,
    QPushButton,
)
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QPen

from .base import UIComponent, Position, UITheme, UIConfig, UIState, CandidateItem,QObjectABCMeta


class CandidateView(QObject, UIComponent, metaclass=QObjectABCMeta):
    """候选列表组件 - 支持多选、预览、图标等"""

    # 自定义信号
    candidate_selected = Signal(str)  # 候选被选中
    candidate_hovered = Signal(str)  # 候选被悬停
    selection_changed = Signal(int)  # 选择变更

    def __init__(self, name: str = "candidate", config: Optional[UIConfig] = None):
        QObject.__init__(self)
        UIComponent.__init__(self, name, config)
        self._widget = None
        self._list_widget = None
        self._header_label = None
        self._candidates: List[CandidateItem] = []
        self._selected_index = -1
        self._hovered_index = -1
        self._max_visible_items = 5
        self._item_height = 40
        self._show_icons = True
        self._show_scores = True
        self._show_descriptions = True
        self._current_theme: Optional[UITheme] = None
        self._animations: Dict[str, QPropertyAnimation] = {}

        self._init_widget()

    def _init_widget(self):
        """初始化组件"""
        self._widget = QWidget()
        self._widget.setObjectName("candidate_view")
        self._widget.setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
        )
        self._widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 创建主布局
        main_layout = QVBoxLayout(self._widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建标题栏
        self._create_header()
        if self._header_label:
            main_layout.addWidget(self._header_label)

        # 创建列表区域
        self._create_list_area()
        if self._list_widget:
            main_layout.addWidget(self._list_widget)

        # 设置样式
        self._update_style()

        # 设置默认大小
        self._widget.resize(350, 250)

    def _create_header(self):
        """创建标题栏"""
        if not self.config.max_candidates:
            return

        self._header_label = QLabel(f"候选词 ({self.config.max_candidates})")
        self._header_label.setObjectName("header_label")
        self._header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._header_label.setFixedHeight(30)

    def _create_list_area(self):
        """创建列表区域"""
        self._list_widget = QListWidget()
        self._list_widget.setObjectName("candidate_list")
        self._list_widget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._list_widget.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._list_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # 连接信号
        self._list_widget.itemClicked.connect(self._on_item_clicked)
        self._list_widget.itemEntered.connect(self._on_item_hovered)
        self._list_widget.currentRowChanged.connect(self._on_selection_changed)

    def show(self, position: Optional[Position] = None) -> None:
        """显示候选列表"""
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

        print(f"Candidate view shown with {len(self._candidates)} items")

    def hide(self) -> None:
        """隐藏候选列表"""
        if not self._widget:
            return

        self.set_state(UIState.HIDDEN)

        # 播放隐藏动画
        self._play_hide_animation()

        print("Candidate view hidden")

    def update_theme(self, theme: UITheme) -> None:
        """更新主题"""
        self._current_theme = theme
        self._update_style()
        print(f"Candidate view theme updated: {theme.name}")

    def set_candidates(self, candidates: List[CandidateItem]) -> None:
        """设置候选列表"""
        self._candidates = candidates[: self.config.max_candidates]
        self._refresh_list()

        # 重置选择
        self._selected_index = -1
        self._hovered_index = -1

        # 更新标题
        if self._header_label:
            self._header_label.setText(f"候选词 ({len(self._candidates)})")

    def add_candidate(self, candidate: CandidateItem) -> None:
        """添加候选"""
        if len(self._candidates) >= self.config.max_candidates:
            return

        self._candidates.append(candidate)
        self._add_list_item(candidate)

        # 更新标题
        if self._header_label:
            self._header_label.setText(f"候选词 ({len(self._candidates)})")

    def clear_candidates(self) -> None:
        """清空候选列表"""
        self._candidates.clear()
        if self._list_widget:
            self._list_widget.clear()

        # 重置选择
        self._selected_index = -1
        self._hovered_index = -1

        # 更新标题
        if self._header_label:
            self._header_label.setText("候选词 (0)")

    def select_next(self) -> None:
        """选择下一个候选"""
        if not self._candidates:
            return

        new_index = (self._selected_index + 1) % len(self._candidates)
        self.set_selected_index(new_index)

    def select_previous(self) -> None:
        """选择上一个候选"""
        if not self._candidates:
            return

        new_index = (self._selected_index - 1) % len(self._candidates)
        self.set_selected_index(new_index)

    def set_selected_index(self, index: int) -> None:
        """设置选中索引"""
        if not self._candidates or index < 0 or index >= len(self._candidates):
            return

        self._selected_index = index

        # 更新UI
        if self._list_widget:
            self._list_widget.setCurrentRow(index)

            # 确保项目在可见区域
            item = self._list_widget.item(index)
            if item:
                self._list_widget.scrollToItem(item)

        # 发出信号
        self.selection_changed.emit(index)

    def get_selected_candidate(self) -> Optional[CandidateItem]:
        """获取当前选中的候选"""
        if 0 <= self._selected_index < len(self._candidates):
            return self._candidates[self._selected_index]
        return None

    def get_preferred_size(self) -> QSize:
        """获取推荐尺寸"""
        if not self._candidates:
            return QSize(300, 100)

        # 计算高度
        visible_items = min(len(self._candidates), self._max_visible_items)
        height = visible_items * self._item_height

        if self._header_label:
            height += 30  # 标题栏高度

        # 添加边距
        height += 20

        return QSize(350, height)

    def set_max_visible_items(self, count: int) -> None:
        """设置最大可见项目数"""
        self._max_visible_items = max(1, count)
        self._update_list_height()

    def enable_icons(self, enabled: bool) -> None:
        """启用/禁用图标显示"""
        self._show_icons = enabled
        self._refresh_list()

    def enable_scores(self, enabled: bool) -> None:
        """启用/禁用分数显示"""
        self._show_scores = enabled
        self._refresh_list()

    def enable_descriptions(self, enabled: bool) -> None:
        """启用/禁用描述显示"""
        self._show_descriptions = enabled
        self._refresh_list()

    def move_to_cursor(self, cursor_pos: Position) -> None:
        """移动到光标位置"""
        if self.config.follow_cursor:
            # 添加偏移量，避免遮挡光标
            offset_pos = Position(cursor_pos.x, cursor_pos.y + 20)
            if self._widget:
                self._widget.move(offset_pos.x, offset_pos.y)

    def _refresh_list(self) -> None:
        """刷新列表显示"""
        if not self._list_widget:
            return

        self._list_widget.clear()

        for candidate in self._candidates:
            self._add_list_item(candidate)

        self._update_list_height()

    def _add_list_item(self, candidate: CandidateItem) -> None:
        """添加列表项"""
        if not self._list_widget:
            return

        # 创建自定义列表项
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, candidate)

        # 创建自定义部件
        item_widget = self._create_candidate_widget(candidate)

        # 设置列表项
        item.setSizeHint(item_widget.sizeHint())
        self._list_widget.addItem(item)
        self._list_widget.setItemWidget(item, item_widget)

    def _create_candidate_widget(self, candidate: CandidateItem) -> QWidget:
        """创建候选部件"""
        widget = QWidget()
        widget.setObjectName("candidate_item")

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # 图标
        if self._show_icons and candidate.icon:
            icon_label = QLabel()
            icon_label.setPixmap(candidate.icon)
            icon_label.setFixedSize(24, 24)
            icon_label.setScaledContents(True)
            layout.addWidget(icon_label)

        # 主要内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)

        # 候选文本
        text_label = QLabel(candidate.text)
        text_label.setObjectName("candidate_text")
        text_label.setFont(
            QFont(
                self._current_theme.font_family if self._current_theme else "Arial",
                self._current_theme.font_size if self._current_theme else 12,
            )
        )
        content_layout.addWidget(text_label)

        # 描述
        if self._show_descriptions and candidate.description:
            desc_label = QLabel(candidate.description)
            desc_label.setObjectName("candidate_description")
            desc_label.setStyleSheet("color: #666666; font-size: 10px;")
            desc_label.setWordWrap(True)
            content_layout.addWidget(desc_label)

        layout.addWidget(content_widget)

        # 分数
        if self._show_scores:
            score_label = QLabel(f"{candidate.score:.2f}")
            score_label.setObjectName("candidate_score")
            score_label.setStyleSheet("color: #999999; font-size: 10px;")
            score_label.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            layout.addWidget(score_label)

        layout.addStretch()

        return widget

    def _update_list_height(self) -> None:
        """更新列表高度"""
        if not self._list_widget:
            return

        visible_items = min(len(self._candidates), self._max_visible_items)
        height = visible_items * self._item_height
        self._list_widget.setFixedHeight(height)

    def _update_style(self) -> None:
        """更新样式"""
        if not self._widget or not self._current_theme:
            return

        style_sheet = f"""
        QWidget#candidate_view {{
            background-color: {self._current_theme.background_color};
            border: 1px solid {self._current_theme.border_color};
            border-radius: 8px;
        }}
        
        QListWidget#candidate_list {{
            background: transparent;
            border: none;
            outline: none;
        }}
        
        QListWidget::item {{
            border: none;
            padding: 5px;
        }}
        
        QListWidget::item:selected {{
            background-color: {self._current_theme.accent_color};
            color: white;
        }}
        
        QListWidget::item:hover {{
            background-color: rgba(128, 128, 128, 30);
        }}
        
        QLabel#header_label {{
            background-color: {self._current_theme.accent_color};
            color: white;
            font-weight: bold;
            padding: 5px;
        }}
        
        QWidget#candidate_item {{
            background: transparent;
        }}
        """

        self._widget.setStyleSheet(style_sheet)

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

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """列表项点击事件"""
        candidate = item.data(Qt.ItemDataRole.UserRole)
        if candidate:
            self.candidate_selected.emit(candidate.text)

    def _on_item_hovered(self, item: QListWidgetItem) -> None:
        """列表项悬停事件"""
        candidate = item.data(Qt.ItemDataRole.UserRole)
        if candidate:
            self.candidate_hovered.emit(candidate.text)

    def _on_selection_changed(self, current_row: int) -> None:
        """选择变更事件"""
        self._selected_index = current_row
        self.selection_changed.emit(current_row)


class SimpleCandidateView:
    """简化版候选列表 - 用于测试"""

    def __init__(self):
        self.candidates: List[CandidateItem] = []
        self.selected_index = -1

    def set_candidates(self, candidates: List[CandidateItem]) -> None:
        """设置候选列表"""
        self.candidates = candidates
        self.selected_index = -1
        print(f"Candidates updated: {[c.text for c in candidates]}")

    def select_next(self) -> None:
        """选择下一个"""
        if not self.candidates:
            return
        self.selected_index = (self.selected_index + 1) % len(self.candidates)
        print(f"Selected: {self.candidates[self.selected_index].text}")

    def select_previous(self) -> None:
        """选择上一个"""
        if not self.candidates:
            return
        self.selected_index = (self.selected_index - 1) % len(self.candidates)
        print(f"Selected: {self.candidates[self.selected_index].text}")

    def get_selected_candidate(self) -> Optional[CandidateItem]:
        """获取当前选中的候选"""
        if 0 <= self.selected_index < len(self.candidates):
            return self.candidates[self.selected_index]
        return None
