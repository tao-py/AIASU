项目结构：

AI Input Assistant Studio Ultimate (AIASU)
│
├─ Inputs
│   ├─ keyboard_listener
│   ├─ voice_input (FastAPI STT)
│   └─ clipboard_monitor
│
├─ Context
│   ├─ app_detector
│   ├─ editor_context
│   ├─ browser_context
│   └─ document_context
│
├─ Ai
│   ├─ agent_router
│   ├─ semantic_agent
│   ├─ code_agent
│   ├─ rag_agent
│   ├─ rewrite_agent
│   └─ candidate_ranker
│
├─ Knowledge
│   ├─ rag_engine
│   ├─ embedding
│   ├─ vector_store
│   └─ indexer
│
├─ Ui
│   ├─ overlay_window
│   ├─ candidate_view
│   ├─ animation_engine
│   └─ ime_window
│
├─ Platform
│   ├─ cursor_anchor
│   ├─ macos_adapter
│   ├─ windows_adapter
│   └─ linux_adapter
│
├─ models (本地已下载的模型)
│   ├─ openai
│
├─ main.py

项目功能：

语义补全
代码补全
RAG知识补全
语音输入
多模型协作
上下文识别
输入法级UI
跨平台运行