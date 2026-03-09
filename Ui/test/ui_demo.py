# Ui/test/ui_demo.py
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 使用绝对导入
from Ui import run_demo

# 运行演示程序
run_demo()