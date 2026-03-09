"""
主题引擎测试
"""

import pytest
import tempfile
import json
from pathlib import Path

from ...theme_engine import ThemeEngine, SimpleThemeEngine
from ...base import UITheme


class TestThemeEngine:
    """主题引擎测试类"""

    @pytest.fixture
    def temp_themes_dir(self):
        """临时主题目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def theme_engine(self, temp_themes_dir):
        """主题引擎实例"""
        return ThemeEngine(temp_themes_dir)

    def test_load_default_theme(self, theme_engine):
        """测试加载默认主题"""
        theme = theme_engine.load_theme("default")

        assert theme.name == "default"
        assert theme.background_color == "#1C1C1E"
        assert theme.text_color == "#FFFFFF"
        assert theme.accent_color == "#007AFF"
        assert theme.opacity == 0.95
        assert theme.border_radius == 12

    def test_load_dark_theme(self, theme_engine):
        """测试加载暗色主题"""
        theme = theme_engine.load_theme("dark")

        assert theme.name == "dark"
        assert theme.background_color == "#000000"
        assert theme.text_color == "#FFFFFF"
        assert theme.accent_color == "#0A84FF"
        assert theme.opacity == 0.98
        assert theme.border_radius == 10

    def test_list_themes(self, theme_engine):
        """测试主题列表"""
        themes = theme_engine.list_themes()

        assert "default" in themes
        assert "dark" in themes
        assert "light" in themes
        assert "glass" in themes
        assert len(themes) >= 4

    def test_create_custom_theme(self, theme_engine):
        """测试创建自定义主题"""
        custom_theme = theme_engine.create_custom_theme(
            "test_custom", "default", background_color="#FF0000", text_color="#00FF00"
        )

        assert custom_theme.name == "test_custom"
        assert custom_theme.background_color == "#FF0000"
        assert custom_theme.text_color == "#00FF00"
        # 其他属性应该继承自默认主题
        assert custom_theme.accent_color == "#007AFF"
        assert custom_theme.opacity == 0.95

    def test_save_and_load_theme(self, theme_engine, temp_themes_dir):
        """测试主题保存和加载"""
        # 创建自定义主题
        custom_theme = UITheme(
            name="test_save",
            background_color="#123456",
            text_color="#654321",
            accent_color="#ABCDEF",
            border_color="#FEDCBA",
            opacity=0.8,
            border_radius=15,
            font_family="TestFont",
            font_size=16,
        )

        # 保存主题
        theme_engine.save_theme(custom_theme)

        # 验证文件存在
        theme_file = Path(temp_themes_dir) / "test_save.json"
        assert theme_file.exists()

        # 加载主题
        loaded_theme = theme_engine.load_theme("test_save")

        assert loaded_theme.name == custom_theme.name
        assert loaded_theme.background_color == custom_theme.background_color
        assert loaded_theme.text_color == custom_theme.text_color
        assert loaded_theme.accent_color == custom_theme.accent_color
        assert loaded_theme.opacity == custom_theme.opacity
        assert loaded_theme.border_radius == custom_theme.border_radius

    def test_delete_theme(self, theme_engine):
        """测试删除主题"""
        # 创建自定义主题
        custom_theme = theme_engine.create_custom_theme("test_delete")

        # 删除主题
        result = theme_engine.delete_theme("test_delete")
        assert result is True

        # 验证主题已被删除
        themes = theme_engine.list_themes()
        assert "test_delete" not in themes

    def test_delete_builtin_theme_fails(self, theme_engine):
        """测试删除内置主题失败"""
        # 尝试删除内置主题
        result = theme_engine.delete_theme("default")
        assert result is False

        # 验证主题仍然存在
        theme = theme_engine.load_theme("default")
        assert theme is not None

    def test_get_theme_preview(self, theme_engine):
        """测试主题预览"""
        preview = theme_engine.get_theme_preview("default")

        assert "name" in preview
        assert "background_color" in preview
        assert "text_color" in preview
        assert "accent_color" in preview
        assert "opacity" in preview
        assert "border_radius" in preview

        assert preview["name"] == "default"
        assert preview["background_color"] == "#1C1C1E"

    def test_validate_theme_success(self, theme_engine):
        """测试主题验证成功"""
        valid_theme = UITheme(
            name="valid",
            background_color="#123456",
            text_color="#654321",
            accent_color="#ABCDEF",
            border_color="#FEDCBA",
            opacity=0.5,
            border_radius=10,
            font_family="Arial",
            font_size=14,
        )

        result = theme_engine.validate_theme(valid_theme)
        assert result is True

    def test_validate_theme_invalid_color(self, theme_engine):
        """测试主题验证失败 - 无效颜色"""
        invalid_theme = UITheme(
            name="invalid_color",
            background_color="invalid_color",
            text_color="#654321",
            accent_color="#ABCDEF",
            border_color="#FEDCBA",
            opacity=0.5,
            border_radius=10,
            font_family="Arial",
            font_size=14,
        )

        result = theme_engine.validate_theme(invalid_theme)
        assert result is False

    def test_validate_theme_invalid_opacity(self, theme_engine):
        """测试主题验证失败 - 无效透明度"""
        invalid_theme = UITheme(
            name="invalid_opacity",
            background_color="#123456",
            text_color="#654321",
            accent_color="#ABCDEF",
            border_color="#FEDCBA",
            opacity=1.5,  # 超出范围
            border_radius=10,
            font_family="Arial",
            font_size=14,
        )

        result = theme_engine.validate_theme(invalid_theme)
        assert result is False

    def test_validate_theme_invalid_border_radius(self, theme_engine):
        """测试主题验证失败 - 无效圆角半径"""
        invalid_theme = UITheme(
            name="invalid_radius",
            background_color="#123456",
            text_color="#654321",
            accent_color="#ABCDEF",
            border_color="#FEDCBA",
            opacity=0.5,
            border_radius=-5,  # 负值
            font_family="Arial",
            font_size=14,
        )

        result = theme_engine.validate_theme(invalid_theme)
        assert result is False

    def test_validate_theme_invalid_font_size(self, theme_engine):
        """测试主题验证失败 - 无效字体大小"""
        invalid_theme = UITheme(
            name="invalid_font_size",
            background_color="#123456",
            text_color="#654321",
            accent_color="#ABCDEF",
            border_color="#FEDCBA",
            opacity=0.5,
            border_radius=10,
            font_family="Arial",
            font_size=0,  # 无效值
        )

        result = theme_engine.validate_theme(invalid_theme)
        assert result is False

    def test_set_current_theme(self, theme_engine):
        """测试设置当前主题"""
        theme = theme_engine.load_theme("dark")
        theme_engine.set_current_theme(theme)

        current_theme = theme_engine.get_current_theme()
        assert current_theme == theme
        assert current_theme.name == "dark"

    def test_theme_persistence(self, theme_engine, temp_themes_dir):
        """测试主题持久化"""
        # 创建自定义主题并保存
        custom_theme = UITheme(
            name="persist_test",
            background_color="#123456",
            text_color="#654321",
            accent_color="#ABCDEF",
            border_color="#FEDCBA",
            opacity=0.8,
            border_radius=15,
            font_family="TestFont",
            font_size=16,
        )
        theme_engine.save_theme(custom_theme)

        # 创建新主题引擎实例
        new_engine = ThemeEngine(temp_themes_dir)

        # 验证之前保存的主题仍然存在
        themes = new_engine.list_themes()
        assert "persist_test" in themes


class TestSimpleThemeEngine:
    """简化版主题引擎测试"""

    def test_simple_theme_engine_creation(self):
        """测试简化版主题引擎创建"""
        engine = SimpleThemeEngine()
        assert engine is not None

    def test_simple_theme_loading(self):
        """测试简化版主题加载"""
        engine = SimpleThemeEngine()
        theme = engine.load_theme("default")

        assert theme.name == "default"
        assert theme.background_color == "#1C1C1E"
        assert theme.text_color == "#FFFFFF"

    def test_simple_theme_list(self):
        """测试简化版主题列表"""
        engine = SimpleThemeEngine()
        themes = engine.list_themes()

        assert "default" in themes
        assert "dark" in themes
        assert "light" in themes

    def test_simple_current_theme(self):
        """测试简化版当前主题"""
        engine = SimpleThemeEngine()
        current_theme = engine.get_current_theme()

        assert current_theme.name == "default"


@pytest.mark.parametrize(
    "color",
    [
        "#123456",  # 标准十六进制
        "#FFFFFF",  # 全大写
        "#000000",  # 全小写
        "rgba(255, 255, 255, 0.5)",  # RGBA
        "rgb(255, 255, 255)",  # RGB
    ],
)
def test_valid_color_formats(color):
    """测试有效颜色格式"""
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = ThemeEngine(temp_dir)
        result = engine._is_valid_color(color)
        assert result is True


@pytest.mark.parametrize(
    "color",
    [
        "#12345",  # 太短
        "#1234567",  # 太长
        "#GGGGGG",  # 无效字符
        "invalid",  # 完全无效
        "rgb(256, 0, 0)",  # 超出范围
        "",  # 空字符串
    ],
)
def test_invalid_color_formats(color):
    """测试无效颜色格式"""
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        engine = ThemeEngine(temp_dir)
        result = engine._is_valid_color(color)
        assert result is False
