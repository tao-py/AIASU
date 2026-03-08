输入 → UI 更新流程

KeyboardListener
│
▼
main.py
│
▼
AgentRouter
│
▼
candidate_ranker
│
▼
OverlayWindow
│
▼
IMEWindow
│
▼
CandidateView


| 模块             | 功能           |
| ---------------- | -------------- |
| overlay_window   | UI 管理器      |
| candidate_view   | 候选列表组件   |
| animation_engine | UI 动画        |
| ime_window       | 输入法候选窗口 |

Ui层目录：
Ui
├─ overlay_window.py
├─ candidate_view.py
├─ animation_engine.py
├─ ime_window.py
└─ menubar_app.py (菜单栏)

输入法级UI，UI 层会基于 PySide6，因为它能实现：
透明窗口
不抢焦点
全局置顶
跟随光标
动画

mac菜单栏运行使用：rumps
实现：后台运行,菜单栏图标

liunx菜单栏运行使用：待定
实现：后台运行,菜单栏图标

windows菜单栏运行使用：待定
实现：后台运行,菜单栏图标
