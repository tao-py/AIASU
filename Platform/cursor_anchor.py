"""
光标锚点 - 跨平台光标位置获取
"""

import sys
import platform

class CursorAnchor:

    def __init__(self):
        self.system = platform.system().lower()
        self.adapter = self._get_adapter()

    def _get_adapter(self):
        """根据平台获取对应的适配器"""
        if self.system == "windows":
            from .windows_adapter import WindowsCursor
            return WindowsCursor()
        elif self.system == "darwin":  # macOS
            from .macos_adapter import MacOSCursor
            return MacOSCursor()
        elif self.system == "linux":
            from .linux_adapter import LinuxCursor
            return LinuxCursor()
        else:
            # 默认返回一个空实现
            return BaseCursor()

    def get_position(self):
        """获取光标位置（跨平台接口）"""
        try:
            pos = self.adapter.get_position()
            # 确保返回的是(x, y)元组
            if isinstance(pos, (tuple, list)) and len(pos) >= 2:
                from Ui.base import Position
                return Position(int(pos[0]), int(pos[1]))
            else:
                return Position(0, 0)
        except Exception as e:
            print(f"Cursor position error: {e}")
            return Position(0, 0)

    def is_available(self):
        """检查适配器是否可用"""
        return self.adapter is not None


class BaseCursor:
    """基础光标类 - 用于不支持的平台"""

    def get_position(self):
        return (0, 0)