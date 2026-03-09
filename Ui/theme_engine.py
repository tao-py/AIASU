import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import asdict

from .base import ThemeManager, UITheme


class ThemeEngine(ThemeManager):
    """主题引擎 - 管理UI主题"""

    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)
        self.themes_dir.mkdir(exist_ok=True)

        self._themes: Dict[str, UITheme] = {}
        self._current_theme: Optional[UITheme] = None

        # 初始化默认主题
        self._init_default_themes()

        # 加载所有主题
        self._load_all_themes()

    def _init_default_themes(self):
        """初始化默认主题"""
        default_themes = {
            "default": UITheme(
                name="default",
                background_color="#1C1C1E",
                text_color="#FFFFFF",
                accent_color="#007AFF",
                border_color="#3A3A3C",
                opacity=0.95,
                border_radius=12,
                font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                font_size=14,
            ),
            "dark": UITheme(
                name="dark",
                background_color="#000000",
                text_color="#FFFFFF",
                accent_color="#0A84FF",
                border_color="#38383A",
                opacity=0.98,
                border_radius=10,
                font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                font_size=14,
            ),
            "light": UITheme(
                name="light",
                background_color="#F2F2F7",
                text_color="#000000",
                accent_color="#007AFF",
                border_color="#C6C6C8",
                opacity=0.95,
                border_radius=12,
                font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                font_size=14,
            ),
            "glass": UITheme(
                name="glass",
                background_color="rgba(255, 255, 255, 0.1)",
                text_color="#FFFFFF",
                accent_color="#007AFF",
                border_color="rgba(255, 255, 255, 0.2)",
                opacity=0.9,
                border_radius=16,
                font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                font_size=14,
            ),
        }

        # 保存默认主题
        for theme_name, theme in default_themes.items():
            self._themes[theme_name] = theme
            self.save_theme(theme)

    def load_theme(self, theme_name: str) -> UITheme:
        """加载主题"""
        if theme_name in self._themes:
            return self._themes[theme_name]

        # 从文件加载
        theme_file = self.themes_dir / f"{theme_name}.json"
        if theme_file.exists():
            try:
                with open(theme_file, "r", encoding="utf-8") as f:
                    theme_data = json.load(f)
                theme = UITheme(**theme_data)
                self._themes[theme_name] = theme
                return theme
            except Exception as e:
                print(f"Error loading theme {theme_name}: {e}")

        # 返回默认主题
        return self._themes["default"]

    def save_theme(self, theme: UITheme) -> None:
        """保存主题"""
        try:
            theme_file = self.themes_dir / f"{theme.name}.json"
            with open(theme_file, "w", encoding="utf-8") as f:
                json.dump(asdict(theme), f, indent=2, ensure_ascii=False)
            self._themes[theme.name] = theme
        except Exception as e:
            print(f"Error saving theme {theme.name}: {e}")

    def list_themes(self) -> List[str]:
        """获取可用主题列表"""
        themes = list(self._themes.keys())

        # 从文件系统加载更多主题
        for theme_file in self.themes_dir.glob("*.json"):
            theme_name = theme_file.stem
            if theme_name not in themes:
                themes.append(theme_name)

        return sorted(themes)

    def get_current_theme(self) -> UITheme:
        """获取当前主题"""
        return self._current_theme or self.load_theme("default")

    def set_current_theme(self, theme: UITheme) -> None:
        """设置当前主题"""
        self._current_theme = theme

    def create_custom_theme(
        self, name: str, base_theme: str = "default", **kwargs
    ) -> UITheme:
        """创建自定义主题"""
        base = self.load_theme(base_theme)

        theme_data = asdict(base)
        theme_data.update(kwargs)
        theme_data["name"] = name

        custom_theme = UITheme(**theme_data)
        self.save_theme(custom_theme)

        return custom_theme

    def delete_theme(self, theme_name: str) -> bool:
        """删除主题"""
        if theme_name in ["default", "dark", "light", "glass"]:
            print(f"Cannot delete built-in theme: {theme_name}")
            return False

        try:
            theme_file = self.themes_dir / f"{theme_name}.json"
            if theme_file.exists():
                theme_file.unlink()

            if theme_name in self._themes:
                del self._themes[theme_name]

            return True
        except Exception as e:
            print(f"Error deleting theme {theme_name}: {e}")
            return False

    def _load_all_themes(self):
        """加载所有主题"""
        for theme_file in self.themes_dir.glob("*.json"):
            theme_name = theme_file.stem
            if theme_name not in self._themes:
                try:
                    with open(theme_file, "r", encoding="utf-8") as f:
                        theme_data = json.load(f)
                    theme = UITheme(**theme_data)
                    self._themes[theme_name] = theme
                except Exception as e:
                    print(f"Error loading theme {theme_name}: {e}")

    def get_theme_preview(self, theme_name: str) -> Dict[str, Any]:
        """获取主题预览信息"""
        theme = self.load_theme(theme_name)

        return {
            "name": theme.name,
            "background_color": theme.background_color,
            "text_color": theme.text_color,
            "accent_color": theme.accent_color,
            "border_color": theme.border_color,
            "opacity": theme.opacity,
            "border_radius": theme.border_radius,
            "font_family": theme.font_family,
            "font_size": theme.font_size,
        }

    def validate_theme(self, theme: UITheme) -> bool:
        """验证主题数据"""
        try:
            # 检查颜色格式
            for color_field in [
                "background_color",
                "text_color",
                "accent_color",
                "border_color",
            ]:
                color = getattr(theme, color_field)
                if not self._is_valid_color(color):
                    print(f"Invalid color format in {color_field}: {color}")
                    return False

            # 检查透明度
            if not (0.0 <= theme.opacity <= 1.0):
                print(f"Invalid opacity value: {theme.opacity}")
                return False

            # 检查圆角半径
            if theme.border_radius < 0:
                print(f"Invalid border radius: {theme.border_radius}")
                return False

            # 检查字体大小
            if theme.font_size <= 0:
                print(f"Invalid font size: {theme.font_size}")
                return False

            return True
        except Exception as e:
            print(f"Error validating theme: {e}")
            return False

    def _is_valid_color(self, color: str) -> bool:
        """验证颜色格式"""
        # 支持多种颜色格式
        # #RRGGBB
        if color.startswith("#") and len(color) == 7:
            try:
                int(color[1:], 16)
                return True
            except ValueError:
                return False

        # rgba(R, G, B, A)
        if color.startswith("rgba(") and color.endswith(")"):
            try:
                # 提取括号内的内容
                inner = color[5:-1]
                values = [v.strip() for v in inner.split(",")]
                if len(values) != 4:
                    return False
                # R, G, B 应该是0-255的整数
                r = int(values[0])
                g = int(values[1])
                b = int(values[2])
                # A 应该是0.0-1.0的浮点数
                a = float(values[3])
                return 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0.0 <= a <= 1.0
            except (ValueError, IndexError):
                return False

        # rgb(R, G, B)
        if color.startswith("rgb(") and color.endswith(")"):
            try:
                # 提取括号内的内容
                inner = color[4:-1]
                values = [v.strip() for v in inner.split(",")]
                if len(values) != 3:
                    return False
                # R, G, B 应该是0-255的整数
                r = int(values[0])
                g = int(values[1])
                b = int(values[2])
                return 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255
            except (ValueError, IndexError):
                return False

        return False


class SimpleThemeEngine:
    """简化版主题引擎 - 用于测试"""

    def __init__(self):
        self._current_theme = "default"
        self._themes = {
            "default": {"name": "default", "background": "#1C1C1E", "text": "#FFFFFF"},
            "dark": {"name": "dark", "background": "#000000", "text": "#FFFFFF"},
            "light": {"name": "light", "background": "#F2F2F7", "text": "#000000"},
        }

    def load_theme(self, theme_name: str) -> UITheme:
        """加载主题"""
        if theme_name in self._themes:
            theme_data = self._themes[theme_name]
            return UITheme(
                name=theme_data["name"],
                background_color=theme_data["background"],
                text_color=theme_data["text"],
                accent_color="#007AFF",
                border_color="#3A3A3C",
                opacity=0.95,
                border_radius=12,
                font_family="Arial",
                font_size=14,
            )
        return self.load_theme("default")

    def list_themes(self) -> List[str]:
        """获取主题列表"""
        return list(self._themes.keys())

    def get_current_theme(self) -> UITheme:
        """获取当前主题"""
        return self.load_theme(self._current_theme)
