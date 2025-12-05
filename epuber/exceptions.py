"""
Epuber 自定义异常类
"""


class EpubError(Exception):
    """EPUB 处理基础异常类"""

    pass


class EpubGenerationError(EpubError):
    """EPUB 生成错误"""

    pass


class EpubValidationError(EpubError):
    """EPUB 验证错误"""

    pass


class FileParseError(EpubError):
    """文件解析错误"""

    pass


class TemplateError(EpubError):
    """模板错误"""

    pass
