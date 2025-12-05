"""
Epuber 文本处理器模块
负责文本内容处理和转换
"""


class TextProcessor:
    """文本处理器类，负责文本到HTML的转换"""

    def __init__(self):
        pass

    def process_content(self, content: str) -> str:
        """
        处理章节内容，转换为 HTML 格式

        Args:
            content: 原始文本内容

        Returns:
            HTML 格式的内容
        """
        if not content.strip():
            return ""

        # 简单的文本到 HTML 转换
        lines = content.split("\n")
        html_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                # 跳过空行，不添加<p></p>
                continue
            else:
                # 转义 HTML 字符
                line = self._escape_html(line)
                html_lines.append(f"<p>{line}</p>")

        return "\n".join(html_lines)

    def _escape_html(self, text: str) -> str:
        """
        转义 HTML 特殊字符

        Args:
            text: 原始文本

        Returns:
            转义后的文本
        """
        return (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;")
                   .replace("'", "&#39;"))
