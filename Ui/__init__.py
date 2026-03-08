"""
AIASU UI层模块

提供完整的输入法级UI解决方案，包括：
- 悬浮窗口 (OverlayWindow)
- 候选列表 (CandidateView)
- 输入法窗口 (IMEWindow)
- 输入预览 (InputPreview)
- UI管理器 (UIManager)
- 动画引擎 (AnimationEngine)
- 主题引擎 (ThemeEngine)
- 配置管理器 (ConfigManager)
- 跨平台菜单栏 (MenuBar)
"""

from .base import (
    UIComponent,
    WindowComponent,
    AnimationController,
    ThemeManager,
    PositionManager,
    UIManagerInterface,
    MenuBarInterface,
    UIState,
    Position,
    UITheme,
    UIConfig,
    CandidateItem,
    UIEvent,
)

from .ui_manager import UIManager, SimpleUIManager
from .overlay_window import OverlayWindow
from .candidate_view import CandidateView
from .ime_window import IMEWindow
from .animation_engine import AnimationEngine, SimpleAnimationEngine
from .theme_engine import ThemeEngine, SimpleThemeEngine
from .config_manager import ConfigManager, SimpleConfigManager
from .input_preview import InputPreview

# 版本信息
__version__ = "1.0.0"
__author__ = "AIASU Team"

# 简化版组件映射
SIMPLE_COMPONENTS = {
    "UIManager": SimpleUIManager,
    "AnimationEngine": SimpleAnimationEngine,
    "ThemeEngine": SimpleThemeEngine,
    "ConfigManager": SimpleConfigManager,
}


def create_ui_manager(
    use_simple: bool = False, config: UIConfig = None
) -> UIManagerInterface:
    """创建UI管理器

    Args:
        use_simple: 是否使用简化版
        config: UI配置

    Returns:
        UI管理器实例
    """
    if use_simple:
        return SimpleUIManager(config)
    return UIManager(config)


def create_animation_engine(use_simple: bool = False) -> AnimationController:
    """创建动画引擎

    Args:
        use_simple: 是否使用简化版

    Returns:
        动画引擎实例
    """
    if use_simple:
        return SimpleAnimationEngine()
    return AnimationEngine()


def create_theme_engine(
    use_simple: bool = False, themes_dir: str = "themes"
) -> ThemeManager:
    """创建主题引擎

    Args:
        use_simple: 是否使用简化版
        themes_dir: 主题目录

    Returns:
        主题引擎实例
    """
    if use_simple:
        return SimpleThemeEngine()
    return ThemeEngine(themes_dir)


def create_config_manager(
    use_simple: bool = False, config_dir: str = "config"
) -> ConfigManager:
    """创建配置管理器

    Args:
        use_simple: 是否使用简化版
        config_dir: 配置目录

    Returns:
        配置管理器实例
    """
    if use_simple:
        return SimpleConfigManager()
    return ConfigManager(config_dir)


def create_default_ui_components(config: UIConfig = None) -> dict:
    """创建默认的UI组件集合

    Args:
        config: UI配置

    Returns:
        包含所有默认组件的字典
    """
    if config is None:
        config = UIConfig()

    return {
        "overlay": OverlayWindow("overlay", config),
        "candidate": CandidateView("candidate", config),
        "ime": IMEWindow("ime", config),
        "preview": InputPreview("preview", config),
    }


def run_tests():
    """运行UI层测试"""
    from .test_framework import run_tests

    run_tests()


def run_demo():
    """运行UI层演示程序"""
    from .test_framework import run_demo

    run_demo()


# 导出主要组件
__all__ = [
    # 基础类和接口
    "UIComponent",
    "WindowComponent",
    "AnimationController",
    "ThemeManager",
    "PositionManager",
    "UIManagerInterface",
    "MenuBarInterface",
    "UIState",
    "Position",
    "UITheme",
    "UIConfig",
    "CandidateItem",
    "UIEvent",
    # 主要组件
    "UIManager",
    "OverlayWindow",
    "CandidateView",
    "IMEWindow",
    "InputPreview",
    "AnimationEngine",
    "ThemeEngine",
    "ConfigManager",
    # 简化版组件
    "SimpleUIManager",
    "SimpleAnimationEngine",
    "SimpleThemeEngine",
    "SimpleConfigManager",
    # 工厂函数
    "create_ui_manager",
    "create_animation_engine",
    "create_theme_engine",
    "create_config_manager",
    "create_default_ui_components",
    # 测试和演示
    "run_tests",
    "run_demo",
    # 版本信息
    "__version__",
    "__author__",
]
