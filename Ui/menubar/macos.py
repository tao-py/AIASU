from typing import Dict, Any
import rumps
import threading
import time

from .base import MenuBarBase


class MacOSMenuBar(MenuBarBase):
    """macOS菜单栏实现 - 使用rumps库"""

    def __init__(self):
        super().__init__()
        self._app = None
        self._menu_items_map = {}

    def _create_native_menu(self) -> Any:
        """创建原生菜单"""
        # 创建应用实例
        self._app = rumps.App("AIASU", "⛩")

        # 创建菜单项
        menu_items = []

        for item_id, item_config in self._menu_items.items():
            if item_config.get("type") == "separator":
                continue

            # 创建菜单项
            title = item_config.get("title", item_id)
            callback = self._callbacks.get(item_id)

            if item_config.get("type") == "checkbox":
                menu_item = rumps.MenuItem(title, callback=callback)
                menu_item.state = 1 if item_config.get("checked", False) else 0
            else:
                menu_item = rumps.MenuItem(title, callback=callback)

            menu_items.append(menu_item)
            self._menu_items_map[item_id] = menu_item

        # 设置菜单
        self._app.menu = menu_items

        return self._app

    def _show_native_notification(
        self, title: str, message: str, duration: int
    ) -> None:
        """显示原生通知"""
        if self._app:
            rumps.notification(title, "", message)

    def _update_native_menu_item(self, item_id: str) -> None:
        """更新原生菜单项"""
        if item_id not in self._menu_items_map:
            return

        menu_item = self._menu_items_map[item_id]
        item_config = self._menu_items[item_id]

        # 更新状态
        if item_config.get("type") == "checkbox":
            menu_item.state = 1 if item_config.get("checked", False) else 0

        # 更新启用状态
        # rumps不直接支持禁用菜单项，这里可以添加其他逻辑

    def _quit_native_menu(self) -> None:
        """退出原生菜单"""
        if self._app:
            rumps.quit_application()

    def _run_native_menu(self) -> None:
        """运行原生菜单"""
        if self._app:
            self._app.run()


def create_default_menu_config() -> Dict[str, Any]:
    """创建默认菜单配置"""
    return {
        "menu_items": {
            "toggle": {"title": "切换显示", "type": "normal"},
            "settings": {"title": "设置", "type": "normal"},
            "separator1": {"type": "separator"},
            "themes": {
                "title": "主题",
                "type": "submenu",
                "items": {
                    "theme_default": {"title": "默认", "type": "radio"},
                    "theme_dark": {"title": "暗色", "type": "radio"},
                    "theme_light": {"title": "亮色", "type": "radio"},
                },
            },
            "separator2": {"type": "separator"},
            "auto_start": {"title": "开机自启", "type": "checkbox"},
            "about": {"title": "关于", "type": "normal"},
            "quit": {"title": "退出", "type": "normal"},
        },
        "callbacks": {
            "toggle": lambda sender: print("Toggle UI"),
            "settings": lambda sender: print("Open settings"),
            "theme_default": lambda sender: print("Set default theme"),
            "theme_dark": lambda sender: print("Set dark theme"),
            "theme_light": lambda sender: print("Set light theme"),
            "auto_start": lambda sender: print("Toggle auto start"),
            "about": lambda sender: print("Show about"),
            "quit": lambda sender: rumps.quit_application(),
        },
    }
