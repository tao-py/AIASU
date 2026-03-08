from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional
import platform
import threading

from .base import MenuBarInterface


class MenuBarBase(MenuBarInterface):
    """菜单栏基类"""

    def __init__(self):
        self._menu_items: Dict[str, Dict[str, Any]] = {}
        self._callbacks: Dict[str, Callable] = {}
        self._is_running = False
        self._thread: Optional[threading.Thread] = None

    @abstractmethod
    def _create_native_menu(self) -> Any:
        """创建原生菜单"""
        pass

    @abstractmethod
    def _show_native_notification(
        self, title: str, message: str, duration: int
    ) -> None:
        """显示原生通知"""
        pass

    def create_menu(self, config: Dict[str, Any]) -> None:
        """创建菜单"""
        self._menu_items = config.get("menu_items", {})
        self._callbacks = config.get("callbacks", {})

        # 创建原生菜单
        self._create_native_menu()

    def update_menu_item(
        self, item_id: str, enabled: bool = True, checked: bool = False
    ) -> None:
        """更新菜单项"""
        if item_id in self._menu_items:
            self._menu_items[item_id]["enabled"] = enabled
            self._menu_items[item_id]["checked"] = checked
            self._update_native_menu_item(item_id)

    def show_notification(self, title: str, message: str, duration: int = 3000) -> None:
        """显示通知"""
        self._show_native_notification(title, message, duration)

    def quit(self) -> None:
        """退出应用"""
        self._is_running = False
        self._quit_native_menu()

    def run(self) -> None:
        """运行菜单栏"""
        if self._is_running:
            return

        self._is_running = True
        self._run_native_menu()

    @abstractmethod
    def _update_native_menu_item(self, item_id: str) -> None:
        """更新原生菜单项"""
        pass

    @abstractmethod
    def _quit_native_menu(self) -> None:
        """退出原生菜单"""
        pass

    @abstractmethod
    def _run_native_menu(self) -> None:
        """运行原生菜单"""
        pass


def create_menubar() -> MenuBarInterface:
    """创建平台相关的菜单栏"""
    system = platform.system()

    if system == "Darwin":  # macOS
        from .macos import MacOSMenuBar

        return MacOSMenuBar()
    elif system == "Windows":
        from .windows import WindowsMenuBar

        return WindowsMenuBar()
    elif system == "Linux":
        from .linux import LinuxMenuBar

        return LinuxMenuBar()
    else:
        # 默认使用通用实现
        from .generic import GenericMenuBar

        return GenericMenuBar()
