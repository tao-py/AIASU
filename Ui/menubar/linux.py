from typing import Dict, Any
import pystray
from PIL import Image, ImageDraw
import threading
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from .base import MenuBarBase


class LinuxMenuBar(MenuBarBase):
    """Linux菜单栏实现 - 使用pystray + AppIndicator3"""

    def __init__(self):
        super().__init__()
        self._tray = None
        self._menu = None
        self._icon = None
        self._indicator = None
        self._message_queue = queue.Queue()
        self._running = False
        self._bus = None
        self._bus_name = None

        # 设置DBus主循环
        DBusGMainLoop(set_as_default=True)

    def _create_native_menu(self) -> Any:
        """创建原生菜单"""
        # 尝试使用AppIndicator3，如果不支持则使用pystray
        try:
            import gi

            gi.require_version("Gtk", "3.0")
            gi.require_version("AppIndicator3", "0.1")
            from gi.repository import Gtk, AppIndicator3

            return self._create_appindicator_menu()
        except (ImportError, ValueError):
            # 回退到pystray
            return self._create_pystray_menu()

    def _create_appindicator_menu(self) -> Any:
        """使用AppIndicator3创建菜单"""
        try:
            import gi

            gi.require_version("Gtk", "3.0")
            gi.require_version("AppIndicator3", "0.1")
            from gi.repository import Gtk, AppIndicator3

            # 创建图标
            self._icon = self._create_default_icon()

            # 创建AppIndicator
            self._indicator = AppIndicator3.Indicator.new(
                "AIASU", "AIASU", AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self._indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

            # 创建菜单
            menu = Gtk.Menu()

            for item_id, item_config in self._menu_items.items():
                if item_config.get("type") == "separator":
                    separator = Gtk.SeparatorMenuItem()
                    menu.append(separator)
                    continue

                title = item_config.get("title", item_id)
                callback = self._callbacks.get(item_id)

                menu_item = Gtk.MenuItem(label=title)

                if callback:
                    menu_item.connect("activate", lambda w, cb=callback: cb(w))

                menu.append(menu_item)

            menu.show_all()
            self._indicator.set_menu(menu)

            return self._indicator

        except Exception as e:
            print(f"AppIndicator3 not available, falling back to pystray: {e}")
            return self._create_pystray_menu()

    def _create_pystray_menu(self) -> Any:
        """使用pystray创建菜单"""
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
        if self._indicator:
            # 使用DBus发送通知
            self._send_dbus_notification(title, message)
        elif self._tray:
            self._tray.notify(message, title)

    def _send_dbus_notification(self, title: str, message: str):
        """通过DBus发送通知"""
        try:
            bus = dbus.SessionBus()
            notify_service = bus.get_object(
                "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
            )
            notify_interface = dbus.Interface(
                notify_service, "org.freedesktop.Notifications"
            )

            notify_interface.Notify(
                "AIASU",  # app_name
                0,  # replaces_id
                "",  # app_icon
                title,  # summary
                message,  # body
                [],  # actions
                {},  # hints
                3000,  # timeout
            )
        except Exception as e:
            print(f"Failed to send DBus notification: {e}")
            # 回退到pystray通知
            if self._tray:
                self._tray.notify(message, title)

    def _update_native_menu_item(self, item_id: str) -> None:
        """更新原生菜单项"""
        self._message_queue.put({"action": "update_menu", "item_id": item_id})

    def _quit_native_menu(self) -> None:
        """退出原生菜单"""
        if self._indicator:
            # GTK应用需要特殊处理
            try:
                from gi.repository import Gtk

                Gtk.main_quit()
            except ImportError:
                pass
        elif self._tray:
            self._tray.stop()

    def _run_native_menu(self) -> None:
        """运行原生菜单"""
        if self._indicator:
            # AppIndicator使用GTK主循环
            try:
                from gi.repository import Gtk

                self._thread = threading.Thread(target=Gtk.main)
                self._thread.daemon = True
                self._thread.start()
            except ImportError:
                pass
        elif self._tray:
            # pystray在新线程中运行
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
