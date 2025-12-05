"""
测试生成器模块
"""

import os
import tempfile
from pathlib import Path

import pytest

from epuber.generator import EpubGenerator
from epuber.parser import Parser
from epuber.processor import TextProcessor

# 可选导入writer
try:
    from epuber.writer import Writer
except ImportError:
    Writer = None


class TestEpubGenerator:
    """测试 EpubGenerator 类"""

    def setup_method(self):
        """测试前准备"""
        self.generator = EpubGenerator()

    def teardown_method(self):
        """测试后清理"""
        pass

    def test_init(self):
        """测试初始化"""
        assert self.generator.parser is not None
        assert self.generator.processor is not None
        # writer在没有ebooklib时为None，这是正常的

    def test_generate_epub_parsing(self):
        """测试EPUB生成时的解析逻辑"""
        content = """第一卷 相遇

小明和小红相遇了...

第1章 初遇

他们第一次见面。

第2章 发展

关系逐渐发展。

番外：回忆

过去的时光...

后记

感谢读者...
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write(content)
            input_file = f.name

        try:
            # 测试解析部分（不实际生成EPUB，因为需要ebooklib）
            volumes = self.generator.parser.parse(Path(input_file))

            # 验证解析结果
            assert len(volumes) == 3  # 第一卷 + 番外 + 后记
            assert volumes[0].title == "第一卷 相遇"
            assert len(volumes[0].chapters) == 3  # 卷标题 + 2章

            # 检查番外
            extra_vol = next(v for v in volumes if "番外" in v.title)
            assert extra_vol.chapters[0].content_type == "extra"

            # 检查后记
            postscript_vol = next(v for v in volumes if "后记" in v.title)
            assert postscript_vol.chapters[0].content_type == "postscript"

        finally:
            os.unlink(input_file)

    def test_generate_epub_parsing_flat(self):
        """测试EPUB生成时的扁平结构解析"""
        content = """第1章 开始

故事开始...

第2章 发展

继续发展...

番外：额外

额外内容...

后记

感谢读者...
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write(content)
            input_file = f.name

        try:
            # 测试解析部分
            volumes = self.generator.parser.parse(Path(input_file))

            # 验证扁平结构解析结果
            assert len(volumes) == 1  # 1个容器包含所有章节
            assert volumes[0].title is None
            assert len(volumes[0].chapters) == 4  # 4个章节

            chapter_titles = [c.title for c in volumes[0].chapters]
            assert "第1章 开始" in chapter_titles
            assert "第2章 发展" in chapter_titles
            assert "番外：额外" in chapter_titles
            assert "后记" in chapter_titles

        finally:
            os.unlink(input_file)

    def test_component_initialization(self):
        """测试组件初始化"""
        assert self.generator.parser is not None
        assert self.generator.processor is not None

        # 验证组件类型
        assert isinstance(self.generator.parser, Parser)
        assert isinstance(self.generator.processor, TextProcessor)

        # writer在没有ebooklib时为None
        if Writer is not None and self.generator.writer is not None:
            assert isinstance(self.generator.writer, Writer)
        elif Writer is None:
            assert self.generator.writer is None

    def test_generate_epub_without_ebooklib(self):
        """测试在没有ebooklib时生成EPUB会抛出错误"""
        content = """第1章 测试

测试内容...
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write(content)
            input_file = f.name

        output_file = Path(tempfile.mktemp(suffix=".epub"))

        try:
            # 如果writer为None，应该抛出错误
            if self.generator.writer is None:
                with pytest.raises(Exception) as exc_info:
                    self.generator.generate_epub(
                        input=Path(input_file), output=output_file, title="测试小说", author="测试作者"
                    )
                assert "ebooklib" in str(exc_info.value)

        finally:
            os.unlink(input_file)
            if output_file.exists():
                os.unlink(output_file)

    def test_validate_epub_nonexistent(self):
        """测试验证不存在的文件"""
        nonexistent = Path("nonexistent.epub")
        assert not self.generator.validate_epub(nonexistent)

    def test_validate_epub_empty_file(self):
        """测试验证空文件"""
        empty_file = Path(tempfile.mktemp(suffix=".epub"))
        try:
            empty_file.touch()  # 创建空文件
            assert not self.generator.validate_epub(empty_file)
        finally:
            if empty_file.exists():
                empty_file.unlink()

    def test_validate_epub_wrong_extension(self):
        """测试验证错误扩展名的文件"""
        wrong_file = Path(tempfile.mktemp(suffix=".txt"))
        try:
            wrong_file.write_text("test")
            assert not self.generator.validate_epub(wrong_file)
        finally:
            if wrong_file.exists():
                wrong_file.unlink()

    def test_validate_epub_valid_mock(self):
        """测试验证有效EPUB文件的逻辑（模拟）"""
        # 创建一个有正确扩展名和大小的假EPUB文件
        valid_epub = Path(tempfile.mktemp(suffix=".epub"))
        try:
            valid_epub.write_bytes(b"fake epub content" * 100)  # 给一些内容
            is_valid = self.generator.validate_epub(valid_epub)
            assert is_valid  # 基本的文件检查应该通过
        finally:
            if valid_epub.exists():
                valid_epub.unlink()
