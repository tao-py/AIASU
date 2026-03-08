from typing import Optional, Dict, Any, Callable, Union
from PySide6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QSequentialAnimationGroup,
    QPoint,
    QRect,
    QSize,
    QTimer,
    QObject,
)
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

from .base import AnimationController, UIComponent, UIConfig


class AnimationEngine(AnimationController):
    """动画引擎 - 提供丰富的UI动画效果"""

    def __init__(self, config: Optional[UIConfig] = None):
        self.config = config
        self._active_animations: Dict[str, QPropertyAnimation] = {}
        self._animation_groups: Dict[
            str, Union[QParallelAnimationGroup, QSequentialAnimationGroup]
        ] = {}
        self._effect_cache: Dict[str, Dict[str, Any]] = {}

    def fade_in(self, component: UIComponent, duration: int = 200) -> None:
        """淡入动画"""
        widget = self._get_widget_from_component(component)
        if not widget:
            return

        # 创建透明度效果
        effect = self._get_or_create_opacity_effect(widget)

        # 创建动画
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 启动动画
        animation.start()

        # 缓存动画
        self._active_animations[f"fade_in_{id(widget)}"] = animation

    def fade_out(self, component: UIComponent, duration: int = 200) -> None:
        """淡出动画"""
        widget = self._get_widget_from_component(component)
        if not widget:
            return

        # 创建透明度效果
        effect = self._get_or_create_opacity_effect(widget)

        # 创建动画
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.Type.InCubic)

        # 启动动画
        animation.start()

        # 缓存动画
        self._active_animations[f"fade_out_{id(widget)}"] = animation

    def slide_in(
        self, component: UIComponent, direction: str = "bottom", duration: int = 200
    ) -> None:
        """滑入动画"""
        widget = self._get_widget_from_component(component)
        if not widget:
            return

        # 获取当前位置
        current_pos = widget.pos()

        # 计算起始位置
        start_pos = self._calculate_slide_start_position(widget, direction)

        # 设置初始位置
        widget.move(start_pos)

        # 创建位置动画
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(current_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutBack)

        # 启动动画
        animation.start()

        # 缓存动画
        self._active_animations[f"slide_in_{id(widget)}"] = animation

    def slide_out(
        self, component: UIComponent, direction: str = "bottom", duration: int = 200
    ) -> None:
        """滑出动画"""
        widget = self._get_widget_from_component(component)
        if not widget:
            return

        # 获取当前位置
        current_pos = widget.pos()

        # 计算结束位置
        end_pos = self._calculate_slide_end_position(widget, direction)

        # 创建位置动画
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(current_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.Type.InBack)

        # 启动动画
        animation.start()

        # 缓存动画
        self._active_animations[f"slide_out_{id(widget)}"] = animation

    def scale_in(self, component: UIComponent, duration: int = 200) -> None:
        """缩放进入动画"""
        widget = self._get_widget_from_component(component)
        if not widget:
            return

        # 创建大小动画
        animation = QPropertyAnimation(widget, b"size")
        animation.setDuration(duration)

        # 设置起始大小（从0开始）
        current_size = widget.size()
        animation.setStartValue(QSize(0, 0))
        animation.setEndValue(current_size)
        animation.setEasingCurve(QEasingCurve.Type.OutElastic)

        # 启动动画
        animation.start()

        # 缓存动画
        self._active_animations[f"scale_in_{id(widget)}"] = animation

    def bounce(self, component: UIComponent, duration: int = 300) -> None:
        """弹跳动画"""
        widget = self._get_widget_from_component(component)
        if not widget:
            return

        # 创建位置动画组
        group = QSequentialAnimationGroup()

        # 向上移动
        up_animation = QPropertyAnimation(widget, b"pos")
        up_animation.setDuration(duration // 2)
        up_animation.setStartValue(widget.pos())
        up_animation.setEndValue(widget.pos() + QPoint(0, -20))
        up_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        # 向下回落
        down_animation = QPropertyAnimation(widget, b"pos")
        down_animation.setDuration(duration // 2)
        down_animation.setStartValue(widget.pos() + QPoint(0, -20))
        down_animation.setEndValue(widget.pos())
        down_animation.setEasingCurve(QEasingCurve.Type.InQuad)

        group.addAnimation(up_animation)
        group.addAnimation(down_animation)

        # 启动动画组
        group.start()

        # 缓存动画组
        self._animation_groups[f"bounce_{id(widget)}"] = group

    def shake(self, component: UIComponent, duration: int = 300) -> None:
        """摇晃动画"""
        widget = self._get_widget_from_component(component)
        if not widget:
            return

        # 创建位置动画组
        group = QSequentialAnimationGroup()

        original_pos = widget.pos()

        # 左右摇晃
        for offset in [-10, 10, -10, 10, -5, 5, -2, 2, 0]:
            anim = QPropertyAnimation(widget, b"pos")
            anim.setDuration(duration // 9)
            anim.setStartValue(widget.pos())
            anim.setEndValue(original_pos + QPoint(offset, 0))
            anim.setEasingCurve(QEasingCurve.Type.Linear)
            group.addAnimation(anim)

        # 启动动画组
        group.start()

        # 缓存动画组
        self._animation_groups[f"shake_{id(widget)}"] = group

    def pulse(self, component: UIComponent, duration: int = 1000) -> None:
        """脉冲动画"""
        widget = self._get_widget_from_component(component)
        if not widget:
            return

        # 创建透明度效果
        effect = self._get_or_create_opacity_effect(widget)

        # 创建动画组
        group = QSequentialAnimationGroup()

        # 淡出
        fade_out = QPropertyAnimation(effect, b"opacity")
        fade_out.setDuration(duration // 2)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.5)
        fade_out.setEasingCurve(QEasingCurve.Type.OutQuad)

        # 淡入
        fade_in = QPropertyAnimation(effect, b"opacity")
        fade_in.setDuration(duration // 2)
        fade_in.setStartValue(0.5)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.InQuad)

        group.addAnimation(fade_out)
        group.addAnimation(fade_in)

        # 启动动画组
        group.start()

        # 缓存动画组
        self._animation_groups[f"pulse_{id(widget)}"] = group

    def glow(
        self,
        component: UIComponent,
        color: Optional[QColor] = None,
        duration: int = 1000,
    ) -> None:
        """发光动画"""
        widget = self._get_widget_from_component(component)
        if not widget:
            return

        # 创建阴影效果
        if color is None:
            color = QColor(100, 150, 255, 200)

        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(color)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

        # 创建模糊半径动画
        animation = QPropertyAnimation(shadow, b"blurRadius")
        animation.setDuration(duration)
        animation.setStartValue(20)
        animation.setEndValue(40)
        animation.setEasingCurve(QEasingCurve.Type.InOutSine)

        # 循环动画
        animation.finished.connect(
            lambda: self._reverse_glow_animation(component, shadow, duration)
        )

        # 启动动画
        animation.start()

        # 缓存动画
        self._active_animations[f"glow_{id(widget)}"] = animation

    def morph(
        self, component: UIComponent, target_size: QSize, duration: int = 300
    ) -> None:
        """变形动画"""
        widget = self._get_widget_from_component(component)
        if not widget:
            return

        # 创建大小动画
        animation = QPropertyAnimation(widget, b"size")
        animation.setDuration(duration)
        animation.setStartValue(widget.size())
        animation.setEndValue(target_size)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # 启动动画
        animation.start()

        # 缓存动画
        self._active_animations[f"morph_{id(widget)}"] = animation

    def stop_animation(
        self, component: UIComponent, animation_type: Optional[str] = None
    ) -> None:
        """停止动画"""
        widget = self._get_widget_from_component(component)
        if not widget:
            return

        widget_id = id(widget)

        if animation_type:
            # 停止指定类型的动画
            key = f"{animation_type}_{widget_id}"
            if key in self._active_animations:
                self._active_animations[key].stop()
                del self._active_animations[key]

            if key in self._animation_groups:
                self._animation_groups[key].stop()
                del self._animation_groups[key]
        else:
            # 停止所有动画
            keys_to_remove = []
            for key in self._active_animations:
                if str(widget_id) in key:
                    self._active_animations[key].stop()
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._active_animations[key]

            keys_to_remove = []
            for key in self._animation_groups:
                if str(widget_id) in key:
                    self._animation_groups[key].stop()
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._animation_groups[key]

    def stop_all_animations(self) -> None:
        """停止所有动画"""
        for animation in self._active_animations.values():
            animation.stop()

        for group in self._animation_groups.values():
            group.stop()

        self._active_animations.clear()
        self._animation_groups.clear()

    # 私有方法
    def _get_widget_from_component(self, component: UIComponent) -> Optional[QWidget]:
        """从组件获取QWidget"""
        try:
            if hasattr(component, "_window") and isinstance(component._window, QWidget):
                return component._window
            elif hasattr(component, "_widget") and isinstance(
                component._widget, QWidget
            ):
                return component._widget
            elif hasattr(component, "_content_widget") and isinstance(
                component._content_widget, QWidget
            ):
                return component._content_widget
            elif isinstance(component, QWidget):
                return component
        except AttributeError:
            pass
        return None

    def _get_or_create_opacity_effect(self, widget: QWidget) -> QGraphicsOpacityEffect:
        """获取或创建透明度效果"""
        widget_id = str(id(widget))

        if widget_id not in self._effect_cache:
            self._effect_cache[widget_id] = {}

        if "opacity" not in self._effect_cache[widget_id]:
            effect = QGraphicsOpacityEffect()
            effect.setOpacity(1.0)
            widget.setGraphicsEffect(effect)
            self._effect_cache[widget_id]["opacity"] = effect

        return self._effect_cache[widget_id]["opacity"]

    def _calculate_slide_start_position(
        self, widget: QWidget, direction: str
    ) -> QPoint:
        """计算滑入起始位置"""
        current_pos = widget.pos()

        if direction == "bottom":
            return QPoint(current_pos.x(), current_pos.y() + 50)
        elif direction == "top":
            return QPoint(current_pos.x(), current_pos.y() - 50)
        elif direction == "left":
            return QPoint(current_pos.x() - 50, current_pos.y())
        elif direction == "right":
            return QPoint(current_pos.x() + 50, current_pos.y())
        else:
            return QPoint(current_pos.x(), current_pos.y() + 50)

    def _calculate_slide_end_position(self, widget: QWidget, direction: str) -> QPoint:
        """计算滑出结束位置"""
        current_pos = widget.pos()

        if direction == "bottom":
            return QPoint(current_pos.x(), current_pos.y() + 50)
        elif direction == "top":
            return QPoint(current_pos.x(), current_pos.y() - 50)
        elif direction == "left":
            return QPoint(current_pos.x() - 50, current_pos.y())
        elif direction == "right":
            return QPoint(current_pos.x() + 50, current_pos.y())
        else:
            return QPoint(current_pos.x(), current_pos.y() + 50)

    def _reverse_glow_animation(
        self, component: UIComponent, shadow: QGraphicsDropShadowEffect, duration: int
    ) -> None:
        """反转发光动画"""
        animation = QPropertyAnimation(shadow, b"blurRadius")
        animation.setDuration(duration)
        animation.setStartValue(40)
        animation.setEndValue(20)
        animation.setEasingCurve(QEasingCurve.Type.InOutSine)

        animation.finished.connect(
            lambda: self.glow(component, shadow.color(), duration)
        )
        animation.start()


class SimpleAnimationEngine:
    """简化版动画引擎 - 用于测试"""

    def __init__(self):
        self._animations = []

    def fade_in(self, component: UIComponent, duration: int = 200) -> None:
        """淡入动画"""
        print(f"Fade in animation (duration: {duration}ms)")

    def fade_out(self, component: UIComponent, duration: int = 200) -> None:
        """淡出动画"""
        print(f"Fade out animation (duration: {duration}ms)")

    def slide_in(
        self, component: UIComponent, direction: str = "bottom", duration: int = 200
    ) -> None:
        """滑入动画"""
        print(f"Slide in animation (direction: {direction}, duration: {duration}ms)")

    def slide_out(
        self, component: UIComponent, direction: str = "bottom", duration: int = 200
    ) -> None:
        """滑出动画"""
        print(f"Slide out animation (direction: {direction}, duration: {duration}ms)")

    def scale_in(self, component: UIComponent, duration: int = 200) -> None:
        """缩放进入动画"""
        print(f"Scale in animation (duration: {duration}ms)")

    def bounce(self, component: UIComponent, duration: int = 300) -> None:
        """弹跳动画"""
        print(f"Bounce animation (duration: {duration}ms)")

    def shake(self, component: UIComponent, duration: int = 300) -> None:
        """摇晃动画"""
        print(f"Shake animation (duration: {duration}ms)")

    def pulse(self, component: UIComponent, duration: int = 1000) -> None:
        """脉冲动画"""
        print(f"Pulse animation (duration: {duration}ms)")

    def glow(
        self,
        component: UIComponent,
        color: Optional[QColor] = None,
        duration: int = 1000,
    ) -> None:
        """发光动画"""
        print(f"Glow animation (color: {color}, duration: {duration}ms)")

    def morph(
        self, component: UIComponent, target_size: QSize, duration: int = 300
    ) -> None:
        """变形动画"""
        print(f"Morph animation (target_size: {target_size}, duration: {duration}ms)")

    def stop_animation(
        self, component: UIComponent, animation_type: Optional[str] = None
    ) -> None:
        """停止动画"""
        if animation_type:
            print(f"Stop {animation_type} animation")
        else:
            print("Stop all animations")

    def stop_all_animations(self) -> None:
        """停止所有动画"""
        print("Stop all animations")
