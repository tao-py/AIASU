# AI Input Assistant Studio Ultimate (AIASU)

**AI驱动的智能输入助手 - 为开发者和专业人士打造**

AIASU是一个先进的AI辅助输入系统，能够根据当前应用上下文提供智能补全、代码建议、知识检索和文本改写。它支持键盘输入、语音输入和剪贴板监控，提供类似输入法的悬浮候选窗口，极大提升输入效率。

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ 核心功能

- **🎯 语义补全** - 基于上下文的智能句子补全
- **💻 代码补全** - 支持Python、JavaScript、Java、C++等多种编程语言
- **📚 RAG知识库** - 从本地文档检索相关信息
- **🎤 语音输入** - 集成Whisper语音识别（需启动STT服务）
- **📋 剪贴板监控** - 自动处理剪贴板内容
- **🖥️ 跨平台** - 支持Windows、macOS、Linux
- **🎨 现代化UI** - 基于Qt的流畅动画和主题系统
- **⚡ 低延迟** - 本地模型运行，响应迅速

## 📁 项目架构

```
AIASU/
├── Inputs/              # 输入源模块
│   ├── keyboard_listener.py    # 键盘监听
│   ├── voice_input.py          # 语音输入（需STT服务）
│   └── clipboard_monitor.py    # 剪贴板监控
├── Context/             # 上下文检测模块
│   ├── app_detector.py         # 应用检测和分类
│   ├── editor_context.py       # 编辑器上下文
│   └── browser_context.py      # 浏览器上下文
├── Ai/                  # AI代理模块
│   ├── agent_router.py         # 代理路由器（协调所有代理）
│   ├── semantic_agent.py       # 语义补全代理
│   ├── code_agent.py           # 代码补全代理
│   ├── rag_agent.py            # RAG知识代理
│   ├── rewrite_agent.py        # 文本改写代理
│   └── candidate_ranker.py     # 候选排序器
├── Knowledge/           # 知识管理模块
│   ├── rag_engine.py           # RAG引擎
│   ├── embedding.py            # embedding模型（sentence-transformers）
│   ├── vector_store.py         # 向量存储（简化实现）
│   └── indexer.py              # 文档索引器
├── Ui/                  # 用户界面模块
│   ├── overlay_window.py       # 悬浮主窗口
│   ├── candidate_view.py       # 候选列表视图
│   ├── animation_engine.py     # 动画引擎
│   ├── ime_window.py           # 输入法窗口
│   ├── base.py                 # UI基类和数据结构
│   ├── config_manager.py       # 配置管理器
│   ├── theme_engine.py         # 主题引擎
│   └── ui_manager.py           # UI管理器
├── Platform/            # 平台适配模块
│   ├── cursor_anchor.py        # 跨平台光标定位
│   ├── windows_adapter.py      # Windows适配器
│   ├── macos_adapter.py        # macOS适配器
│   └── linux_adapter.py        # Linux适配器
├── Api/                 # API服务模块
│   └── STT.py                  # 语音识别API（FastAPI + Whisper）
├── models/              # 本地模型目录
│   └── openai/                 # OpenAI模型（如Whisper）
├── data/                # 数据目录（自动生成）
│   └── vector_store.pkl       # 向量数据库
├── main.py              # 主程序入口
├── mind.md              # 设计文档
├── requirements.txt     # Python依赖
└── README.md            # 本文档
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.11 或更高版本
- **操作系统**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 20.04+)
- **内存**: 最少 4GB RAM（推荐 8GB+）
- **磁盘**: 至少 2GB 可用空间

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/yourusername/AIASU.git
cd AIASU
```

2. **创建虚拟环境**

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **使用uv安装依赖**（推荐）

```bash
uv pip install -r requirements.txt
```

或者使用pip：

```bash
pip install -r requirements.txt
```

4. **下载模型文件**（可选）

如果使用本地Whisper模型，请将模型文件放置在 `models/openai/` 目录下：

```bash
mkdir -p models/openai
# 下载whisper-small等模型到该目录
```

5. **初始化知识库**（可选）

如果需要使用RAG功能，可以添加文档到知识库：

```python
from Knowledge.indexer import DocumentIndexer

indexer = DocumentIndexer()
indexer.index_directory("./docs")  # 索引文档目录
```

### 运行程序

```bash
# 激活虚拟环境（如果尚未激活）
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 运行主程序
python main.py
```

程序启动后：

- 会显示一个悬浮窗口（初始可能最小化）
- 开始监听键盘输入
- 输入文字后按空格键，会显示候选建议
- 使用数字键1-5或鼠标选择候选

### 启动语音识别服务（可选）

如果需要语音输入功能，需要先启动STT服务：

```bash
# 在另一个终端窗口运行
uv run python Api/STT.py
```

或者在代码中：

```python
from Api.STT import VoiceTypingApp, run_api_server

app = VoiceTypingApp(model_path="./models/openai/whisper-small")
run_api_server(app, host="127.0.0.1", port=8000)
```

## 🎯 使用方法

### 基本操作

1. **启动程序** - 运行 `python main.py`
2. **开始输入** - 在任意应用（编辑器、浏览器、终端等）中输入文字
3. **查看候选** - 输入完成后按空格键，悬浮窗口会显示候选建议
4. **选择候选** - 按数字键1-5或点击鼠标选择
5. **隐藏窗口** - 选择后窗口自动隐藏

### 应用类型支持

- **编辑器/IDE** - 提供代码补全、语义补全
- **浏览器** - 提供网页内容相关的补全
- **终端** - 提供命令补全
- **办公软件** - 提供邮件、文档相关的补全
- **通用** - 基础的语义补全和改写

### 知识库使用

1. **添加文档**

```python
from Knowledge.rag_engine import RagEngine

rag = RagEngine()
rag.add_document("Python是一种高级编程语言...", {"category": "programming"})
```

2. **使用索引器批量添加**

```python
from Knowledge.indexer import DocumentIndexer

indexer = DocumentIndexer()
indexer.index_directory("./my_documents")
```

### 配置自定义

编辑 `Ui/config_manager.py` 或创建配置文件来自定义：

- 主题颜色
- 窗口透明度
- 动画效果开关
- 最大候选数量
- 自动隐藏延迟

## 🔧 技术实现

### 关键技术栈

- **UI框架**: PySide6 (Qt6)
- **AI模型**: sentence-transformers (all-MiniLM-L6-v2)
- **向量存储**: 自定义numpy+pickle实现
- **语音识别**: OpenAI Whisper (Transformers)
- **API框架**: FastAPI
- **进程监控**: psutil
- **输入监控**: pynput, pyperclip

### 核心设计理念

1. **模块化架构** - 每个组件独立，便于维护和扩展
2. **跨平台兼容** - 通过适配器模式支持多平台
3. **本地优先** - 模型在本地运行，保护隐私
4. **低耦合** - 组件间通过清晰接口通信
5. **可扩展** - 易于添加新的AI代理和输入源

### 候选生成流程

```
输入 → 上下文检测 → Agent路由 → 
├─ 语义代理 → 句子补全
├─ 代码代理 → 代码片段（仅编辑器）
├─ RAG代理 → 知识检索
├─ 改写代理 → 文本变体
└─ 排序器 → 语义相似度排序
```

## 📦 依赖包说明

主要依赖（详见requirements.txt）：


| 包名                  | 用途                 | 版本    |
| --------------------- | -------------------- | ------- |
| PySide6               | GUI框架              | 6.6.0   |
| sentence-transformers | Embedding模型        | 2.2.2   |
| numpy                 | 数值计算             | 1.24.3  |
| chromadb              | 向量数据库（未使用） | 0.4.15  |
| fastapi               | Web API框架          | 0.104.1 |
| transformers          | Hugging Face模型     | 4.35.0  |
| torch                 | 深度学习框架         | 2.1.0   |
| pynput                | 键盘/鼠标监听        | 1.7.6   |
| pyperclip             | 剪贴板操作           | 1.8.2   |
| psutil                | 进程管理             | 5.9.5   |

**注意**: 当前实现使用简化向量存储，不依赖chromadb。如需使用chromadb，请安装onnxruntime。

## 🛠️ 开发指南

### 项目结构说明

- **Inputs/**: 输入处理，支持多种输入方式
- **Context/**: 上下文感知，检测当前应用和环境
- **Ai/**: AI代理系统，每个代理专注于特定任务
- **Knowledge/**: 知识管理，RAG和向量存储
- **Ui/**: 用户界面，基于Qt的组件库
- **Platform/**: 平台抽象层，统一跨平台接口
- **Api/**: 外部API服务，如语音识别

### 添加新的AI代理

1. 在 `Ai/` 目录创建 `xxx_agent.py`
2. 实现 `run(text, context)` 方法，返回 `List[CandidateItem]`
3. 在 `agent_router.py` 的 `AgentRouter` 类中注册

示例：

```python
from Ui.base import CandidateItem

class MyAgent:
    def run(self, text: str, context: dict = None) -> List[CandidateItem]:
        # 实现你的逻辑
        return [
            CandidateItem(text="候选1", score=0.8),
            CandidateItem(text="候选2", score=0.6)
        ]
```

### 添加新的输入源

1. 在 `Inputs/` 目录创建 `xxx_input.py`
2. 实现 `start()` 和 `stop()` 方法
3. 在 `main.py` 中实例化并启动

示例：

```python
class MyInput:
    def __init__(self, callback):
        self.callback = callback
        self.running = False

    def start(self):
        self.running = True
        # 启动监听线程

    def stop(self):
        self.running = False
```

### 自定义UI组件

所有UI组件继承自 `Ui.base` 中的抽象基类：

- `UIComponent` - 基础组件
- `WindowComponent` - 窗口组件
- `CandidateView` - 候选视图（已实现）

实现必要抽象方法：

```python
class MyComponent(UIComponent):
    def show(self, position=None):
        pass

    def hide(self):
        pass

    def update_theme(self, theme):
        pass

    def get_preferred_size(self):
        pass
```

## 🐛 故障排除

### 常见问题

**Q: 程序启动后没有反应？**
A: 检查是否激活了虚拟环境，确保所有依赖已安装。

**Q: 候选窗口不显示？**
A: 确保输入了文字并按空格键。检查应用检测是否正常工作。

**Q: 语音识别无法使用？**
A: 需要先启动STT服务：`python Api/STT.py`。确保安装了Whisper模型。

**Q: embedding模型下载慢？**
A: 第一次运行会自动下载all-MiniLM-L6-v2模型，约100MB。可以手动下载到缓存目录。

**Q: 在macOS上权限问题？**
A: 需要授权辅助功能权限：系统偏好设置 → 安全性与隐私 → 辅助功能。

**Q: Linux下缺少库？**
A: 安装系统依赖：`sudo apt-get install python3-xlib libxcb-xinerama0`

### 调试模式

启用调试日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

查看详细输出，帮助定位问题。

## 📝 测试

运行单元测试：

```bash
cd Ui/test
python run_tests.py
```

运行集成测试：

```bash
python test_modules.py
```

## 🔮 未来计划

- [ ]  集成更多LLM（GPT、Claude、本地LLM）
- [ ]  支持多轮对话上下文
- [ ]  添加用户配置文件系统
- [ ]  实现插件系统
- [ ]  优化性能（缓存、异步处理）
- [ ]  添加更多主题和自定义选项
- [ ]  支持更多编程语言
- [ ]  云端同步用户配置

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers) - Embedding模型
- [Qt](https://www.qt.io/) - 跨平台GUI框架
- [PySide6](https://wiki.qt.io/Qt_for_Python) - Python绑定

## 📧 联系方式

- 作者: Bottao
- 邮箱: myaide@outlook.com
- 项目主页: https://github.com/tao-py/AIASU.git
- 问题反馈: https://github.com/yourusername/AIASU/issues

---

**享受智能输入的乐趣！** 🎉
