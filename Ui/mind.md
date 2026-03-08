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
└─ ime_window.py

UI 层会基于 PySide6，因为它能实现：
透明窗口
不抢焦点
全局置顶
跟随光标
动画



### mac菜单栏运行

使用：

<pre class="overflow-visible! px-0!" data-start="4059" data-end="4072"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼ5 ͼj"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>rumps</span></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

实现：

<pre class="overflow-visible! px-0!" data-start="4079" data-end="4102"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute end-1.5 top-1 z-2 md:end-2 md:top-1"></div><div class="pt-3"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼ5 ͼj"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>后台运行</span><br/><span>菜单栏图标</span><br/><span>AI助手</span></div></div></div></div></div></div></div></div></div></div></div></div></pre>
