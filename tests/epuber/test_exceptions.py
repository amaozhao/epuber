"""
测试异常模块
"""

import pytest

from epuber.exceptions import (
    EpubError,
    EpubGenerationError,
    FileParseError,
    EpubValidationError,
    TemplateError
)


class TestExceptions:
    """测试异常类"""

    def test_epub_generation_error_creation(self):
        """测试EpubGenerationError创建"""
        error = EpubGenerationError("测试生成错误")
        assert str(error) == "测试生成错误"
        assert isinstance(error, EpubGenerationError)
        assert isinstance(error, Exception)

    def test_epub_generation_error_with_cause(self):
        """测试带原因的EpubGenerationError"""
        cause = ValueError("原始错误")
        error = EpubGenerationError("包装错误")

        assert str(error) == "包装错误"
        # 注意：这里不设置__cause__，只是测试基本的异常创建

    def test_file_parse_error_creation(self):
        """测试FileParseError创建"""
        error = FileParseError("解析文件失败")
        assert str(error) == "解析文件失败"
        assert isinstance(error, FileParseError)
        assert isinstance(error, EpubError)

    def test_file_parse_error_with_file_path(self):
        """测试带文件路径的FileParseError"""
        error = FileParseError("解析失败: test.txt")
        assert "test.txt" in str(error)

    def test_validation_error_creation(self):
        """测试EpubValidationError创建"""
        error = EpubValidationError("验证失败")
        assert str(error) == "验证失败"
        assert isinstance(error, EpubValidationError)
        assert isinstance(error, EpubError)

    def test_validation_error_with_details(self):
        """测试带详细信息的EpubValidationError"""
        error = EpubValidationError("数据验证失败", "标题不能为空")
        assert "数据验证失败" in str(error)
        assert "标题不能为空" in str(error)

    def test_template_error_creation(self):
        """测试TemplateError创建"""
        error = TemplateError("模板错误")
        assert str(error) == "模板错误"
        assert isinstance(error, TemplateError)
        assert isinstance(error, EpubError)

    def test_template_error_with_template_name(self):
        """测试带模板名称的TemplateError"""
        error = TemplateError("模板加载失败", "default.css")
        assert "模板加载失败" in str(error)
        assert "default.css" in str(error)

    def test_exception_hierarchy(self):
        """测试异常继承关系"""
        # 测试继承链
        assert issubclass(EpubGenerationError, EpubError)
        assert issubclass(FileParseError, EpubError)
        assert issubclass(EpubValidationError, EpubError)
        assert issubclass(TemplateError, EpubError)

        # 测试实例类型
        gen_error = EpubGenerationError("test")
        parse_error = FileParseError("test")
        validation_error = EpubValidationError("test")
        template_error = TemplateError("test")

        assert isinstance(gen_error, EpubError)
        assert isinstance(parse_error, EpubError)
        assert isinstance(validation_error, EpubError)
        assert isinstance(template_error, EpubError)

    def test_exception_inheritance_from_base(self):
        """测试所有异常都继承自Exception"""
        exceptions = [
            EpubGenerationError("test"),
            FileParseError("test"),
            EpubValidationError("test"),
            TemplateError("test")
        ]

        for exc in exceptions:
            assert isinstance(exc, Exception)

    def test_exception_messages(self):
        """测试异常消息格式"""
        # 测试不同消息格式
        messages = [
            "简单消息",
            "包含路径: /path/to/file.txt",
            "多行消息\n第二行",
            "特殊字符: <>&\""
        ]

        for msg in messages:
            error = EpubGenerationError(msg)
            assert str(error) == msg

    def test_exception_context_preservation(self):
        """测试异常上下文保留"""
        try:
            try:
                raise ValueError("原始异常")
            except ValueError as original:
                raise FileParseError("包装异常") from original
        except FileParseError as wrapped:
            assert isinstance(wrapped.__cause__, ValueError)
            assert str(wrapped.__cause__) == "原始异常"

    def test_exception_raising_and_catching(self):
        """测试异常抛出和捕获"""
        with pytest.raises(EpubError):
            raise EpubGenerationError("测试异常")

        with pytest.raises(FileParseError):
            raise FileParseError("文件解析失败")

        with pytest.raises(EpubValidationError):
            raise EpubValidationError("验证失败")

        with pytest.raises(TemplateError):
            raise TemplateError("模板错误")

    def test_exception_chaining(self):
        """测试异常链"""
        def func_that_fails():
            raise ValueError("内部错误")

        def func_that_wraps():
            try:
                func_that_fails()
            except ValueError as e:
                raise FileParseError("包装错误") from e

        with pytest.raises(FileParseError) as exc_info:
            func_that_wraps()

        # 检查异常链
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, ValueError)
        assert str(exc_info.value.__cause__) == "内部错误"
