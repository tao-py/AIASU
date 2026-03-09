"""
浏览器上下文检测模块
"""

class BrowserContext:

    def __init__(self):
        self.browser_processes = [
            "chrome.exe", "chrome", "chromium.exe", "chromium",
            "firefox.exe", "firefox",
            "msedge.exe", "msedge", "edge.exe", "edge",
            "safari.exe", "safari",
            "opera.exe", "opera",
            "brave.exe", "brave"
        ]

    def get_context(self, url=None, title=None, selection=None):
        """获取浏览器上下文信息"""
        context = {
            "type": "browser",
            "url": url or "",
            "title": title or "",
            "domain": self._extract_domain(url) if url else "",
            "selection": selection or "",
            "page_type": self._classify_page(url, title)
        }
        return context

    def _extract_domain(self, url):
        """从URL提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""

    def _classify_page(self, url, title):
        """分类页面类型"""
        if not url and not title:
            return "unknown"

        combined = (url + title).lower()

        # 开发/文档类
        dev_keywords = ["github", "stackoverflow", "docs", "documentation", "api", "reference", "tutorial"]
        if any(keyword in combined for keyword in dev_keywords):
            return "development"

        # 代码托管
        code_hosts = ["github.com", "gitlab.com", "bitbucket.org"]
        if any(host in combined for host in code_hosts):
            return "code_hosting"

        # 社交媒体
        social = ["facebook", "twitter", "linkedin", "instagram", "tiktok", "weibo"]
        if any(s in combined for s in social):
            return "social"

        # 视频/媒体
        media = ["youtube.com", "bilibili.com", "netflix", "twitch", "vimeo"]
        if any(m in combined for m in media):
            return "media"

        # 搜索
        search = ["google.com/search", "baidu.com/s", "bing.com/search"]
        if any(s in combined for s in search):
            return "search"

        # 邮箱
        email = ["mail.google", "outlook.live", "mail.yahoo", "protonmail"]
        if any(e in combined for e in email):
            return "email"

        return "general"