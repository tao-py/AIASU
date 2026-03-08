# UI层设计思路

## 输入 → UI 更新流程

```
KeyboardListener
│
▼
main.py
│
▼
UIManager (新增)
│
▼
OverlayWindow
│
▼
CandidateView
│
▼
IMEWindow
```

## 核心模块

| 模块             | 功能                    | 状态   |
| ---------------- | ----------------------- | ------ |
| ui_manager       | UI协调器，统一管理      | 新增   |
| overlay_window   | 透明悬浮窗口            | 已有   |
| candidate_view   | 候选列表展示组件        | 已有   |
| ime_window       | 输入法候选窗口          | 已有   |
| animation_engine | UI动画引擎              | 已有   |
| theme_engine     | 主题管理器              | 新增   |
| input_preview    | 输入预览组件            | 新增   |
| config_manager   | UI配置持久化            | 新增   |

## UI层目录结构

```
Ui/
├── ui_manager.py          # UI协调器
├── overlay_window.py      # 悬浮窗口
├── candidate_view.py      # 候选列表
├── ime_window.py          # 输入法窗口
├── animation_engine.py    # 动画引擎
├── theme_engine.py        # 主题管理
├── input_preview.py       # 输入预览
├── config_manager.py      # 配置管理
├── menubar/
│   ├── __init__.py
│   ├── base.py           # 抽象基类
│   ├── macos.py          # macOS实现 (rumps)
│   ├── windows.py        # Windows实现
│   └── linux.py          # Linux实现
└── themes/
    ├── default.json      # 默认主题
    ├── dark.json         # 暗色主题
    └── custom/           # 用户自定义主题
```

## 技术栈

- **GUI框架**: PySide6
  - 跨平台一致性
  - 支持透明窗口
  - 不抢夺焦点
  - 全局置顶
  - 光标跟随
  - 流畅动画

## 核心特性

### 1. 智能定位
- 光标跟随算法
- 多显示器适配
- 边界检测（防止窗口超出屏幕）

### 2. 视觉体验
- 毛玻璃背景效果
- 平滑动画过渡
- 主题切换（深色/浅色/自定义）
- 字体自适应

### 3. 交互优化
- 鼠标悬停预览
- 键盘导航支持
- 触摸板手势
- 快捷键管理

### 4. 跨平台菜单栏

#### macOS
- 使用 `rumps` 库
- 系统托盘集成
- 原生菜单风格

#### Windows
- 使用 `pystray` + `PIL`
- 系统通知区域
- 跳转列表支持

#### Linux
- 使用 `pystray` + `AppIndicator3`
- 兼容主流桌面环境
- D-Bus集成

## 配置管理

```json
{
  "ui": {
    "theme": "auto",
    "opacity": 0.95,
    "animation_duration": 200,
    "max_candidates": 5,
    "window_padding": 8,
    "font_size": 14,
    "follow_cursor": true,
    "multi_monitor": true
  },
  "shortcuts": {
    "toggle_ui": "Ctrl+Shift+Space",
    "next_theme": "Ctrl+Shift+T",
    "settings": "Ctrl+Shift+,"
  }
}
```

## 开发规范

1. **组件化**: 每个UI组件独立可复用
2. **响应式**: 适配不同屏幕尺寸
3. **无障碍**: 支持屏幕阅读器
4. **性能**: 异步渲染，避免阻塞
5. **主题化**: 所有颜色通过主题引擎管理
