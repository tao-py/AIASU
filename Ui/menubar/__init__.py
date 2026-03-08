"""
跨平台菜单栏模块
提供统一的菜单栏接口，支持macOS、Windows和Linux
"""

from .base import MenuBarBase, create_menubar
from .macos import MacOSMenuBar, create_default_menu_config as macos_menu_config
from .windows import WindowsMenuBar, create_default_menu_config as windows_menu_config
from .linux import LinuxMenuBar, create_default_menu_config as linux_menu_config

# 平台特定的菜单栏配置
PLATFORM_MENU_CONFIGS = {
    "Darwin": macos_menu_config,
    "Windows": windows_menu_config,
    "Linux": linux_menu_config,
}


def get_platform_menu_config():
    """获取当前平台的菜单配置"""
    import platform

    system = platform.system()
    return PLATFORM_MENU_CONFIGS.get(system, linux_menu_config)


def create_platform_menubar():
    """创建平台相关的菜单栏"""
    return create_menubar()


# 导出主要组件
__all__ = [
    "MenuBarBase",
    "MacOSMenuBar",
    "WindowsMenuBar",
    "LinuxMenuBar",
    "create_menubar",
    "create_platform_menubar",
    "get_platform_menu_config",
    "PLATFORM_MENU_CONFIGS",
]
