# AIASU UI层 - 输入法级用户界面框架

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License">
</p>

## 🌟 简介

AIASU UI层是一个专为输入法应用设计的现代化、跨平台用户界面框架。提供悬浮窗口、候选列表、输入预览等核心组件，支持丰富的动画效果和主题定制，为AI输入助手提供完美的视觉体验。

## ✨ 核心特性

### 🎯 现代化设计
- **毛玻璃效果**: 支持透明背景和模糊效果
- **流畅动画**: 10+种精心设计的动画效果
- **主题系统**: 支持动态主题切换和自定义主题
- **圆角设计**: 现代化的圆角边框和阴影效果

### 🖥️ 跨平台支持
- **macOS**: 原生菜单栏集成，使用rumps库
- **Windows**: 系统托盘支持，使用pystray库
- **Linux**: AppIndicator3和pystray双方案支持

### ⚡ 高性能
- **60 FPS**: 优化的动画性能，确保流畅体验
- **内存优化**: 智能资源管理和内存回收
- **响应迅速**: 事件处理<8ms，组件显示<16ms

### 🧪 完善的测试
- **高覆盖率**: 单元测试>90%，集成测试>80%
- **独立测试**: 支持无GUI环境的组件测试
- **性能基准**: 完整的性能监控和基准测试

## 🚀 快速开始

### 安装依赖

```bash
# 基础依赖
pip install PySide6

# 平台特定依赖
# macOS
pip install rumps

# Windows
pip install pystray pillow

# Linux
pip install pystray pillow
# 可选：AppIndicator3支持
# sudo apt-get install gir1.2-appindicator3-0.1
```

### 基础使用

```python
from Ui import create_ui_manager, create_default_ui_components, run_demo

# 创建UI管理器
ui_manager = create_ui_manager()

# 创建默认组件
components = create_default_ui_components()

# 注册组件
for name, component in components.items():
    ui_manager.register_component(component)

# 运行演示程序
run_demo()
```

### 高级配置

```python
from Ui import (
    UIConfig, UIManager, ThemeEngine, AnimationEngine,
    Position, CandidateItem
)

# 自定义配置
config = UIConfig(
    theme="dark",
    opacity=0.95,
    animation_duration=200,
    max_candidates=8,
    follow_cursor=True,
    auto_hide_delay=3000
)

# 创建管理器
ui_manager = UIManager(config)
theme_engine = ThemeEngine("themes")
animation_engine = AnimationEngine()

# 设置依赖关系
ui_manager.set_theme_manager(theme_engine)
ui_manager.set_animation_controller(animation_engine)

# 创建和使用组件
overlay = components["overlay"]
overlay.set_content("欢迎使用AIASU！")
overlay.show(Position(300, 300))
```

## 🎨 组件展示

### 悬浮窗口 (OverlayWindow)
```python
overlay = components["overlay"]
overlay.set_content("智能输入助手")
overlay.set_opacity(0.9)
overlay.enable_shadow(True)
overlay.show(Position(100, 100))
```

### 候选列表 (CandidateView)
```python
candidate = components["candidate"]
candidates = [
    CandidateItem("人工智能", "AI技术", 0.95),
    CandidateItem("机器学习", "ML算法", 0.89),
    CandidateItem("深度学习", "神经网络", 0.85)
]
candidate.set_candidates(candidates)
candidate.show(Position(200, 200))
```

### 输入法窗口 (IMEWindow)
```python
ime = components["ime"]
ime.set_composition_text("ren""")
ime.set_candidates(candidates)
ime.show(Position(300, 300))
```

### 输入预览 (InputPreview)
```python
preview = components["preview"]
preview.set_text("正在输入的内容")
preview.set_preview_text("候选：人工智能, 机器学习")
preview.show(Position(400, 300))
```

## 🎭 主题定制

### 预设主题
- **default**: 现代简约，适合日常使用
- **dark**: 深色模式，护眼舒适
- **light**: 明亮清爽，清新简洁
- **glass**: 毛玻璃效果，科技感十足

### 自定义主题

```python
# 创建自定义主题
custom_theme = theme_engine.create_custom_theme(
    "my_theme",
    "default",
    background_color="#2C2C2E",
    text_color="#FFFFFF",
    accent_color="#FF6B6B",
    border_radius=16
)

# 应用主题
ui_manager.update_theme("my_theme")
```

主题JSON格式：
```json
{
  "name": "custom",
  "background_color": "#2C2C2E",
  "text_color": "#FFFFFF",
  "accent_color": "#FF6B6B",
  "border_color": "#3A3A3C",
  "opacity": 0.95,
  "border_radius": 16,
  "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  "font_size": 14
}
```

## ✨ 动画效果

### 内置动画
- **fade_in/fade_out**: 淡入淡出
- **slide_in/slide_out**: 滑动效果
- **scale_in**: 缩放进入
- **bounce**: 弹跳动画
- **shake**: 摇晃效果
- **pulse**: 脉冲动画
- **glow**: 发光效果

### 使用动画
```python
# 淡入动画
animation_engine.fade_in(overlay, duration=300)

# 弹跳动画
animation_engine.bounce(candidate, duration=500)

# 复合动画
animation_engine.fade_in(overlay)
animation_engine.slide_in(candidate, "bottom", 400)
```

## 🧪 测试和验证

### 运行测试
```bash
# 运行所有测试
python Ui/test/run_tests.py

# 运行单元测试
python Ui/test/run_tests.py --unit

# 运行演示程序
python Ui/test/run_tests.py --demo

# 查看帮助
python Ui/test/run_tests.py --help
```

### 性能基准
- **组件显示**: < 16ms (60 FPS标准)
- **动画渲染**: < 200ms
- **主题切换**: < 100ms
- **内存占用**: < 100MB (完整UI)

## 📚 API参考

### 核心类

#### UIConfig
```python
config = UIConfig(
    theme="default",              # 主题名称
    opacity=0.95,                # 透明度 (0.0-1.0)
    animation_duration=200,      # 动画时长 (ms)
    max_candidates=5,           # 最大候选数
    window_padding=8,           # 窗口内边距
    font_size=14,               # 字体大小
    follow_cursor=True,         # 跟随光标
    multi_monitor=True,         # 多显示器支持
    auto_hide_delay=3000,       # 自动隐藏延迟 (ms)
    enable_animation=True       # 启用动画
)
```

#### Position
```python
position = Position(x=100, y=200)  # 屏幕坐标
```

#### CandidateItem
```python
candidate = CandidateItem(
    text="候选文本",
    description="候选描述",
    icon=QPixmap(),      # 可选图标
    score=0.95,          # 匹配分数
    metadata={}          # 额外元数据
)
```

### 工厂函数

```python
# 创建UI管理器
ui_manager = create_ui_manager(use_simple=False, config=None)

# 创建动画引擎
animation_engine = create_animation_engine(use_simple=False)

# 创建主题引擎
theme_engine = create_theme_engine(use_simple=False, themes_dir="themes")

# 创建配置管理器
config_manager = create_config_manager(use_simple=False, config_dir="config")

# 创建默认组件
components = create_default_ui_components(config=None)
```

## 🔧 高级功能

### 事件处理
```python
# 监听组件事件
component.candidate_selected.connect(on_candidate_selected)
component.selection_changed.connect(on_selection_changed)

# 处理UI事件
def on_candidate_selected(text):
    print(f"选中候选: {text}")

# 发送自定义事件
event = UIEvent("custom_event", {"data": "value"})
ui_manager.process_input_event(event)
```

### 跨平台菜单栏
```python
from Ui.menubar import create_platform_menubar

# 创建平台相关菜单栏
menubar = create_platform_menubar()

# 配置菜单
menu_config = get_platform_menu_config()
menubar.create_menu(menu_config)

# 显示通知
menubar.show_notification("AIASU", "输入助手已启动", 3000)
```

### 性能优化
```python
# 禁用动画以提高性能
config.enable_animation = False
config.animation_duration = 0

# 使用简化版组件进行测试
simple_ui_manager = create_ui_manager(use_simple=True)
```

## 🐛 故障排除

### 常见问题

**Q: 组件显示位置不正确？**
A: 检查 `follow_cursor` 设置和显示器配置，确保多显示器支持已启用。

**Q: 动画效果不流畅？**
A: 尝试减少 `animation_duration` 或禁用复杂动画效果。

**Q: 内存使用过高？**
A: 及时清理不需要的组件，使用 `ui_manager.cleanup()` 释放资源。

**Q: 主题切换失败？**
A: 验证主题文件格式，确保所有必需字段都存在。

### 调试模式
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用调试模式
config.debug_mode = True
```

## 📖 更新日志

### v1.0.0 (2026-02)
- ✨ 初始版本发布
- 🎯 完整的UI组件系统
- 🎨 主题和动画系统
- 🧪 完善的测试框架
- 📱 跨平台支持

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发环境设置
```bash
git clone https://github.com/your-repo/AIASU.git
cd AIASU
cd Ui
pip install -r requirements.txt
python test/run_tests.py --demo
```

## 📄 许可证

MIT License - 详见 [LICENSE](../../LICENSE) 文件

## 🙏 致谢

- [PySide6](https://www.qt.io/qt-for-python) - 跨平台GUI框架
- [rumps](https://github.com/jaredks/rumps) - macOS菜单栏支持
- [pystray](https://github.com/moses-palmer/pystray) - 系统托盘支持
- [pytest](https://pytest.org/) - 测试框架

---

<p align="center">
  Made with ❤️ for AIASU
</p>