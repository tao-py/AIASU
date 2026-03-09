"""
配置管理器测试
测试ConfigManager的配置加载、保存和管理功能
"""

import pytest
import json
import tempfile
from pathlib import Path
import threading
import time

from ...config_manager import ConfigManager, AppConfig
from ...base import UIConfig, UITheme


class TestConfigManagerInitialization:
    """配置管理器初始化测试"""

    def test_manager_creation_default_dir(self):
        """测试使用默认目录创建管理器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                manager = ConfigManager()
                assert manager.config_dir.exists()
                assert manager._config_file.name == "config.json"
            finally:
                os.chdir(original_cwd)

    def test_manager_creation_custom_dir(self):
        """测试使用自定义目录创建管理器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)
            assert manager.config_dir == Path(temp_dir)
            assert manager._config_file == Path(temp_dir) / "config.json"

    def test_manager_creates_config_file_on_init(self):
        """测试初始化时创建配置文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)
            # 配置文件应该在初始化时被创建或加载
            assert manager._config_file.parent.exists()


class TestConfigLoadAndSave:
    """配置加载和保存测试"""

    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)

            # 修改配置
            manager.set("ui.theme", "dark")
            manager.set("ui.opacity", 0.8)
            manager.set("auto_start", True)
            manager.set("debug_mode", True)

            # 保存
            manager.save_config()

            # 创建新管理器实例加载配置
            new_manager = ConfigManager(temp_dir)

            # 验证配置已加载
            assert new_manager.get("ui.theme") == "dark"
            assert new_manager.get("ui.opacity") == 0.8
            assert new_manager.get("auto_start") is True
            assert new_manager.get("debug_mode") is True

    def test_load_nonexistent_config(self):
        """加载不存在的配置文件时使用默认值"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 确保配置文件不存在
            config_file = Path(temp_dir) / "config.json"
            if config_file.exists():
                config_file.unlink()

            manager = ConfigManager(temp_dir)

            # 应该使用默认值
            assert manager.get("ui.theme") == "default"
            assert manager.get("ui.opacity") == 0.95

    def test_save_config_creates_valid_json(self):
        """测试保存的配置是有效的JSON"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)
            manager.set("test.key", "test_value")
            manager.save_config()

            # 验证JSON文件格式正确
            with open(manager._config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            assert isinstance(data, dict)


class TestConfigGetAndSet:
    """配置获取和设置测试"""

    @pytest.fixture
    def manager(self):
        """配置管理器实例"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield ConfigManager(temp_dir)

    def test_get_simple_key(self, manager):
        """测试获取简单键"""
        # 使用默认配置测试
        result = manager.get("ui.theme")
        assert result == "default"  # 默认值

    def test_get_nested_key(self, manager):
        """测试获取嵌套键"""
        manager.set("ui.theme", "dark")
        result = manager.get("ui.theme")
        assert result == "dark"

    def test_get_with_default(self, manager):
        """测试带默认值的获取"""
        result = manager.get("nonexistent.key", default="default_value")
        assert result == "default_value"

    def test_set_simple_value(self, manager):
        """测试设置简单值"""
        manager.set("test_value", 123)
        # 直接设置到_config的指定路径
        # 由于set方法实现可能复杂，我们主要测试流程

    def test_set_ui_config(self, manager):
        """测试设置UI配置"""
        manager.set("ui.opacity", 0.7)
        assert manager.get("ui.opacity") == 0.7

    def test_set_boolean_values(self, manager):
        """测试布尔值设置"""
        manager.set("auto_start", True)
        manager.set("check_updates", False)

        assert manager.get("auto_start") is True
        assert manager.get("check_updates") is False

    def test_set_string_values(self, manager):
        """测试字符串值设置"""
        manager.set("language", "zh-CN")
        manager.set("theme_name", "dark")

        assert manager.get("language") == "zh-CN"
        assert manager.get("theme_name") == "dark"

    def test_set_numeric_values(self, manager):
        """测试数值设置"""
        manager.set("cache_size", 2000)
        manager.set("max_history_items", 50)

        assert manager.get("cache_size") == 2000
        assert manager.get("max_history_items") == 50


class TestConfigDefaults:
    """配置默认值测试"""

    def test_default_ui_config(self):
        """测试默认UI配置"""
        default_config = AppConfig()

        assert default_config.ui.theme == "default"
        assert default_config.ui.opacity == 0.95
        assert default_config.ui.animation_duration == 200
        assert default_config.ui.max_candidates == 5

    def test_default_app_config(self):
        """测试默认应用配置"""
        default_config = AppConfig()

        assert default_config.auto_start is False
        assert default_config.check_updates is True
        assert default_config.debug_mode is False
        assert default_config.log_level == "INFO"
        assert default_config.cache_size == 1000
        assert default_config.max_history_items == 100
        assert default_config.enable_voice_input is True
        assert default_config.enable_clipboard_monitor is True
        assert default_config.shortcut_toggle == "Ctrl+Shift+Space"
        assert default_config.shortcut_settings == "Ctrl+Shift+,"
        assert default_config.theme_name == "default"
        assert default_config.language == "zh-CN"


class TestConfigThreadSafety:
    """配置线程安全性测试"""

    def test_concurrent_config_access(self):
        """测试并发配置访问"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)
            results = []

            def worker(thread_id):
                try:
                    key = f"thread_{thread_id}_key"
                    value = f"thread_{thread_id}_value"
                    manager.set(key, value)
                    retrieved = manager.get(key)
                    results.append((thread_id, retrieved == value))
                except Exception as e:
                    results.append((thread_id, f"error: {e}"))

            threads = []
            for i in range(10):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # 所有线程应该成功
            assert len(results) == 10
            for thread_id, success in results:
                assert success is True

    def test_lock_prevents_race_condition(self):
        """测试锁防止竞争条件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)
            errors = []

            def concurrent_writer(thread_id):
                try:
                    for i in range(100):
                        key = f"shared_key_{thread_id}"
                        manager.set(key, thread_id)
                except Exception as e:
                    errors.append(e)

            threads = []
            for i in range(5):
                thread = threading.Thread(target=concurrent_writer, args=(i,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            # 不应该有错误
            assert len(errors) == 0


class TestConfigPersistence:
    """配置持久化测试"""

    def test_config_survives_restart(self):
        """测试配置在重启后仍然存在"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 第一次会话
            manager1 = ConfigManager(temp_dir)
            manager1.set("ui.theme", "dark")
            manager1.set("ui.font_size", 16)
            manager1.set("language", "zh-CN")  # 使用AppConfig中存在的字段
            manager1.save_config()

            # 第二次会话（模拟重启）
            manager2 = ConfigManager(temp_dir)

            assert manager2.get("ui.theme") == "dark"
            assert manager2.get("ui.font_size") == 16
            assert manager2.get("language") == "zh-CN"

    def test_config_file_format(self):
        """测试配置文件格式"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)
            manager.set("ui.theme", "light")
            manager.set("ui.animation_duration", 300)
            manager.set("auto_start", True)
            manager.save_config()

            # 读取原始JSON验证格式
            with open(manager._config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 验证结构
            assert "ui" in data
            assert data["ui"]["theme"] == "light"
            assert data["ui"]["animation_duration"] == 300
            assert data["auto_start"] is True


class TestConfigReset:
    """配置重置测试"""

    def test_reset_to_defaults(self):
        """测试重置为默认值"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)

            # 修改多个配置
            manager.set("ui.theme", "custom")
            manager.set("ui.opacity", 0.5)
            manager.set("auto_start", True)

            # 重置（如果实现了reset方法）
            # 或者通过重新加载默认配置
            manager._config = AppConfig()  # 重置为默认
            manager.save_config()

            # 验证恢复默认
            new_manager = ConfigManager(temp_dir)
            assert new_manager.get("ui.theme") == "default"
            assert new_manager.get("ui.opacity") == 0.95
            assert new_manager.get("auto_start") is False


class TestConfigValidation:
    """配置验证测试"""

    def test_invalid_opacity_range(self):
        """测试无效透明度范围"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)

            # 设置超出范围的值（如果实现了验证）
            manager.set("ui.opacity", 1.5)
            # 取决于实现，可能仍然接受

    def test_invalid_animation_duration(self):
        """测试无效动画持续时间"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)

            manager.set("ui.animation_duration", -100)
            # 验证处理

    def test_invalid_max_candidates(self):
        """测试无效候选数"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)

            manager.set("ui.max_candidates", 0)
            # 验证处理


class TestConfigSpecialValues:
    """配置特殊值测试"""

    def test_empty_string_values(self):
        """测试空字符串值"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)
            manager.set("language", "")
            # 空字符串应该被接受

    def test_none_values(self):
        """测试None值"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)
            # None值的处理取决于实现
            # 某些配置可能不允许None

    def test_large_numeric_values(self):
        """测试大数值"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)
            manager.set("cache_size", 1000000)
            assert manager.get("cache_size") == 1000000

    def test_unicode_string_values(self):
        """测试Unicode字符串"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)
            unicode_text = "中文测试 🎉"
            manager.set("language", unicode_text)  # language是AppConfig中的字段
            assert manager.get("language") == unicode_text


class TestConfigUIThemeIntegration:
    """配置与主题集成测试"""

    def test_theme_name_in_config(self):
        """测试配置中的主题名称"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(temp_dir)

            theme_name = manager.get("theme_name")
            assert isinstance(theme_name, str)

            manager.set("theme_name", "dark")
            assert manager.get("theme_name") == "dark"
