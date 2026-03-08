import json
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import asdict, dataclass, field
import threading

from .base import UIConfig, UITheme


@dataclass
class AppConfig:
    """应用配置数据类"""

    ui: UIConfig = field(default_factory=UIConfig)
    auto_start: bool = False
    check_updates: bool = True
    debug_mode: bool = False
    log_level: str = "INFO"
    cache_size: int = 1000
    max_history_items: int = 100
    enable_voice_input: bool = True
    enable_clipboard_monitor: bool = True
    shortcut_toggle: str = "Ctrl+Shift+Space"
    shortcut_settings: str = "Ctrl+Shift+,"
    theme_name: str = "default"
    language: str = "zh-CN"


class ConfigManager:
    """配置管理器 - 统一管理应用配置"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        self._config_file = self.config_dir / "config.json"
        self._lock = threading.Lock()

        # 默认配置
        self._default_config = AppConfig()
        self._config = AppConfig()

        # 加载配置
        self.load_config()

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        with self._lock:
            keys = key.split(".")
            value = self._config

            try:
                for k in keys:
                    if isinstance(value, dict):
                        value = value[k]
                    else:
                        value = getattr(value, k)
                return value
            except (KeyError, AttributeError):
                return default

    def set(self, key: str, value: Any) -> bool:
        """设置配置项"""
        with self._lock:
            try:
                keys = key.split(".")
                target = self._config

                # 导航到父级
                for k in keys[:-1]:
                    if isinstance(target, dict):
                        target = target[k]
                    else:
                        target = getattr(target, k)

                # 设置最终值
                if isinstance(target, dict):
                    target[keys[-1]] = value
                else:
                    setattr(target, keys[-1], value)

                # 保存配置
                self.save_config()
                return True

            except Exception as e:
                print(f"Error setting config {key}: {e}")
                return False

    def get_ui_config(self) -> UIConfig:
        """获取UI配置"""
        return self._config.ui

    def set_ui_config(self, config: UIConfig) -> bool:
        """设置UI配置"""
        self._config.ui = config
        return self.save_config()

    def get_theme_name(self) -> str:
        """获取主题名称"""
        return self._config.theme_name

    def set_theme_name(self, theme_name: str) -> bool:
        """设置主题名称"""
        self._config.theme_name = theme_name
        return self.save_config()

    def get_shortcut(self, action: str) -> str:
        """获取快捷键"""
        if action == "toggle":
            return self._config.shortcut_toggle
        elif action == "settings":
            return self._config.shortcut_settings
        return ""

    def set_shortcut(self, action: str, shortcut: str) -> bool:
        """设置快捷键"""
        if action == "toggle":
            self._config.shortcut_toggle = shortcut
        elif action == "settings":
            self._config.shortcut_settings = shortcut
        else:
            return False

        return self.save_config()

    def load_config(self) -> bool:
        """加载配置"""
        try:
            if not self._config_file.exists():
                # 创建默认配置
                self.save_config()
                return True

            with open(self._config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # 创建新的配置对象
            new_config = AppConfig()

            # 更新UI配置
            if "ui" in config_data:
                ui_data = config_data["ui"]
                new_config.ui = UIConfig(**ui_data)

            # 更新其他配置
            for key, value in config_data.items():
                if key != "ui" and hasattr(new_config, key):
                    setattr(new_config, key, value)

            self._config = new_config
            return True

        except Exception as e:
            print(f"Error loading config: {e}")
            # 使用默认配置
            self._config = AppConfig()
            return False

    def save_config(self) -> bool:
        """保存配置"""
        try:
            config_data = asdict(self._config)

            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        self._config = AppConfig()
        return self.save_config()

    def export_config(self, file_path: str) -> bool:
        """导出配置"""
        try:
            config_data = asdict(self._config)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error exporting config: {e}")
            return False

    def import_config(self, file_path: str) -> bool:
        """导入配置"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # 验证配置数据
            if self._validate_config(config_data):
                # 创建新的配置对象
                new_config = AppConfig()

                # 更新配置
                for key, value in config_data.items():
                    if hasattr(new_config, key):
                        setattr(new_config, key, value)

                self._config = new_config
                return self.save_config()
            else:
                print("Invalid config data")
                return False

        except Exception as e:
            print(f"Error importing config: {e}")
            return False

    def _validate_config(self, config_data: Dict[str, Any]) -> bool:
        """验证配置数据"""
        required_fields = ["ui", "theme_name", "language"]

        for field in required_fields:
            if field not in config_data:
                print(f"Missing required field: {field}")
                return False

        # 验证UI配置
        if "ui" in config_data:
            ui_config = config_data["ui"]
            required_ui_fields = ["theme", "opacity", "animation_duration"]
            for field in required_ui_fields:
                if field not in ui_config:
                    print(f"Missing required UI field: {field}")
                    return False

        return True

    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return asdict(self._config)

    def update_config(self, config_data: Dict[str, Any]) -> bool:
        """更新配置"""
        try:
            # 验证配置
            if not self._validate_config(config_data):
                return False

            # 创建新的配置对象
            new_config = AppConfig()

            # 更新配置
            for key, value in config_data.items():
                if hasattr(new_config, key):
                    setattr(new_config, key, value)

            self._config = new_config
            return self.save_config()

        except Exception as e:
            print(f"Error updating config: {e}")
            return False

    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "theme_name": self._config.theme_name,
            "language": self._config.language,
            "auto_start": self._config.auto_start,
            "debug_mode": self._config.debug_mode,
            "enable_voice_input": self._config.enable_voice_input,
            "enable_clipboard_monitor": self._config.enable_clipboard_monitor,
            "shortcut_toggle": self._config.shortcut_toggle,
            "ui_opacity": self._config.ui.opacity,
            "ui_animation_duration": self._config.ui.animation_duration,
            "max_history_items": self._config.max_history_items,
        }


class SimpleConfigManager:
    """简化版配置管理器 - 用于测试"""

    def __init__(self):
        self._config = {
            "theme_name": "default",
            "language": "zh-CN",
            "auto_start": False,
            "debug_mode": False,
            "ui": {
                "theme": "default",
                "opacity": 0.95,
                "animation_duration": 200,
                "max_candidates": 5,
                "window_padding": 8,
                "font_size": 14,
                "follow_cursor": True,
                "multi_monitor": True,
                "auto_hide_delay": 3000,
                "enable_animation": True,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> bool:
        """设置配置项"""
        try:
            keys = key.split(".")
            target = self._config

            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]

            target[keys[-1]] = value
            return True

        except Exception as e:
            print(f"Error setting config {key}: {e}")
            return False

    def get_ui_config(self) -> UIConfig:
        """获取UI配置"""
        ui_data = self.get("ui", {})
        return UIConfig(**ui_data)

    def get_theme_name(self) -> str:
        """获取主题名称"""
        return self.get("theme_name", "default")

    def get_shortcut(self, action: str) -> str:
        """获取快捷键"""
        if action == "toggle":
            return "Ctrl+Shift+Space"
        elif action == "settings":
            return "Ctrl+Shift+,"
        return ""
