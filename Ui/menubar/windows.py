from typing import Dict, Any
import pystray
from PIL import Image, ImageDraw
import threading
import queue

from .base import MenuBarBase


class WindowsMenuBar(MenuBarBase):
    """Windows菜单栏实现 - 使用pystray库"""

    def __init__(self):
        super().__init__()
        self._tray = None
        self._menu = None
        self._icon = None
        self._message_queue = queue.Queue()
        self._running = False

    def _create_native_menu(self) -> Any:
        """创建原生菜单"""
        # 创建图标
        self._icon = self._create_default_icon()

        # 创建菜单项
        menu_items = []

        for item_id, item_config in self._menu_items.items():
            if item_config.get("type") == "separator":
                menu_items.append(pystray.Menu.SEPARATOR)
                continue

            title = item_config.get("title", item_id)
            callback = self._callbacks.get(item_id)

            if item_config.get("type") == "checkbox":
                menu_item = pystray.MenuItem(
                    title,
                    callback,
                    checked=lambda item: item_config.get("checked", False),
                )
            elif item_config.get("type") == "radio":
                menu_item = pystray.MenuItem(title, callback, radio=True)
            else:
                menu_item = pystray.MenuItem(title, callback)

            menu_items.append(menu_item)

        # 创建菜单
        self._menu = pystray.Menu(*menu_items)

        # 创建系统托盘图标
        self._tray = pystray.Icon("AIASU", self._icon, "AIASU - AI输入助手", self._menu)

        return self._tray

    def _show_native_notification(
        self, title: str, message: str, duration: int
    ) -> None:
        """显示原生通知"""
        if self._tray:
            self._tray.notify(message, title)

    def _update_native_menu_item(self, item_id: str) -> None:
        """更新原生菜单项"""
        # pystray的菜单项更新需要重新创建菜单
        # 这里使用消息队列来更新
        self._message_queue.put({"action": "update_menu", "item_id": item_id})

    def _quit_native_menu(self) -> None:
        """退出原生菜单"""
        if self._tray:
            self._tray.stop()

    def _run_native_menu(self) -> None:
        """运行原生菜单"""
        if self._tray:
            # 在新线程中运行托盘图标
            self._thread = threading.Thread(target=self._tray.run)
            self._thread.daemon = True
            self._thread.start()

    def _create_default_icon(self) -> Image.Image:
        """创建默认图标"""
        # 创建一个简单的图标
        width = 64
        height = 64

        image = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(image)

        # 绘制一个简单的图标（字母A）
        draw.rectangle([0, 0, width - 1, height - 1], outline="blue", width=2)
        draw.text((width // 2 - 8, height // 2 - 8), "A", fill="blue")

        return image

    def _process_message_queue(self):
        """处理消息队列"""
        try:
            while True:
                message = self._message_queue.get_nowait()
                self._handle_message(message)
        except queue.Empty:
            pass

    def _handle_message(self, message: Dict[str, Any]):
        """处理消息"""
        action = message.get("action")

        if action == "update_menu":
            # 重新创建菜单以更新状态
            self._create_native_menu()


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
            "quit": lambda sender: print("Quit application"),
        },
    }
