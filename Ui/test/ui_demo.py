# Ui/test/ui_demo.py
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 使用绝对导入
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