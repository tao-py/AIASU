import psutil
import os
import sys

class AppDetector:

    def detect(self):
        """检测当前活动应用的信息"""
        try:
            process = psutil.Process()
            name = process.name()
            exe = process.exe() if hasattr(process, 'exe') else ""
            cmdline = process.cmdline()

            # 获取父进程
            try:
                parent = process.parent()
                parent_name = parent.name() if parent else "unknown"
            except:
                parent_name = "unknown"

            # 判断应用类型
            app_type = self._classify_app(name, exe, cmdline, parent_name)

            return {
                "name": name,
                "exe": exe,
                "type": app_type,
                "parent": parent_name
            }
        except Exception as e:
            print(f"App detection error: {e}")
            return {
                "name": "unknown",
                "exe": "",
                "type": "unknown",
                "parent": "unknown"
            }

    def _classify_app(self, name, exe, cmdline, parent_name):
        """分类应用类型"""
        name_lower = name.lower()
        exe_lower = exe.lower() if exe else ""
        parent_lower = parent_name.lower()

        # 编辑器类
        editors = ["code", "vscode", "sublime", "notepad++", "notepad", "vim", "nvim", "emacs"]
        if any(editor in name_lower or editor in exe_lower for editor in editors):
            return "editor"

        # IDE类
        ides = ["idea", "pycharm", "eclipse", "androidstudio", "visualstudio", "devenv"]
        if any(ide in name_lower or ide in exe_lower for ide in ides):
            return "ide"

        # 浏览器类
        browsers = ["chrome", "firefox", "edge", "safari", "opera", "msedge", "chromium"]
        if any(browser in name_lower or browser in exe_lower for browser in browsers):
            return "browser"

        # 终端类
        terminals = ["cmd", "powershell", "bash", "zsh", "fish", "conhost", "terminal"]
        if any(term in name_lower or term in parent_lower for term in terminals):
            return "terminal"

        # 办公软件
        office = ["winword", "excel", "powerpoint", "outlook", "libreoffice", "wps"]
        if any(office_app in name_lower or office_app in exe_lower for office_app in office):
            return "office"

        return "general"