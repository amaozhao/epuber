"""
测试文本处理器模块
"""

from epuber.processor import TextProcessor


class TestTextProcessor:
    """测试 TextProcessor 类"""

    def setup_method(self):
        """测试前准备"""
        self.processor = TextProcessor()

    def teardown_method(self):
        """测试后清理"""
        pass

    def test_init(self):
        """测试初始化"""
        processor = TextProcessor()
        assert processor is not None

    def test_process_content_basic(self):
        """测试基本内容处理"""
        content = """第一行文本
第二行文本

空行后的文本"""

        result = self.processor.process_content(content)

        # 检查基本 HTML 结构
        assert "<p>第一行文本</p>" in result
        assert "<p>第二行文本</p>" in result
        assert "<p>空行后的文本</p>" in result

    def test_process_content_empty_lines(self):
        """测试空行处理"""
        content = """文本

空行

更多文本"""

        result = self.processor.process_content(content)

        # 空行应该被跳过，不产生<p></p>
        assert "<p></p>" not in result
        assert result == "<p>文本</p>\n<p>空行</p>\n<p>更多文本</p>"

    def test_process_content_special_chars(self):
        """测试特殊字符转义"""
        content = """文本包含<>&"符号"""

        result = self.processor.process_content(content)

        # 检查 HTML 转义
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result
        assert "&quot;" in result

    def test_process_content_empty(self):
        """测试空内容"""
        result = self.processor.process_content("")
        assert result == ""

    def test_process_content_single_line(self):
        """测试单行内容"""
        content = "单行内容"
        result = self.processor.process_content(content)
        assert "<p>单行内容</p>" in result

    def test_escape_html(self):
        """测试HTML转义方法"""
        # 测试 < 转义
        assert self.processor._escape_html("a<b") == "a&lt;b"
        # 测试 > 转义
        assert self.processor._escape_html("a>b") == "a&gt;b"
        # 测试 & 转义
        assert self.processor._escape_html("a&b") == "a&amp;b"
        # 测试组合转义
        assert self.processor._escape_html("<>&") == "&lt;&gt;&amp;"

    def test_process_content_chinese_chars(self):
        """测试中文字符处理"""
        content = """中文内容
第二行中文

空行后的中文"""

        result = self.processor.process_content(content)

        # 检查中文字符保持不变
        assert "中文内容" in result
        assert "第二行中文" in result
        assert "空行后的中文" in result
        # 检查HTML结构
        assert "<p>" in result
        assert "</p>" in result
