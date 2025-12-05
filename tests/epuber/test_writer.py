"""
测试写入器模块
"""

import tempfile
from pathlib import Path

import pytest

from epuber.schemas import Chapter, Volume

# 可选导入Writer和ebooklib
try:
    from ebooklib import epub

    from epuber.writer import Writer

    HAS_EBOOKLIB = True
except ImportError:
    Writer = None
    epub = None
    HAS_EBOOKLIB = False


class TestWriter:
    """测试 Writer 类"""

    def setup_method(self):
        """测试前准备"""
        if not HAS_EBOOKLIB:
            pytest.skip("ebooklib not available, skipping Writer tests")
        self.writer = Writer()

    def teardown_method(self):
        """测试后清理"""
        pass

    def test_init(self):
        """测试初始化"""
        writer = Writer()
        assert writer.template_dir is not None
        assert writer.template_dir.name == "templates"

    def test_write_epub_basic(self):
        """测试基本EPUB写入"""
        # 创建测试数据
        chapter = Chapter(title="测试章节", content="<p>测试内容</p>", content_type="chapter")
        volume = Volume(title="测试卷", chapters=[chapter])

        output_file = Path(tempfile.mktemp(suffix=".epub"))

        try:
            self.writer.write_epub(volumes=[volume], output=output_file, title="测试小说", author="测试作者")

            # 检查输出文件
            assert output_file.exists()
            assert output_file.stat().st_size > 0

        finally:
            if output_file.exists():
                output_file.unlink()

    def test_write_epub_multiple_volumes(self):
        """测试多卷EPUB写入"""
        volumes = []

        # 创建多个卷
        for i in range(1, 3):
            chapter = Chapter(title=f"第{i}章", content=f"<p>第{i}章内容</p>", content_type="chapter")
            volume = Volume(title=f"第{i}卷", chapters=[chapter])
            volumes.append(volume)

        output_file = Path(tempfile.mktemp(suffix=".epub"))

        try:
            self.writer.write_epub(volumes=volumes, output=output_file, title="多卷测试小说", author="测试作者")

            assert output_file.exists()
            assert output_file.stat().st_size > 0

        finally:
            if output_file.exists():
                output_file.unlink()

    def test_write_epub_with_cover(self):
        """测试带封面的EPUB写入"""
        chapter = Chapter(title="测试章节", content="<p>测试内容</p>", content_type="chapter")
        volume = Volume(title="测试卷", chapters=[chapter])

        # 创建临时封面文件
        cover_file = Path(tempfile.mktemp(suffix=".png"))
        cover_file.write_bytes(b"fake png data")

        output_file = Path(tempfile.mktemp(suffix=".epub"))

        try:
            self.writer.write_epub(
                volumes=[volume], output=output_file, title="测试小说", author="测试作者", cover=cover_file
            )

            assert output_file.exists()

        finally:
            if cover_file.exists():
                cover_file.unlink()
            if output_file.exists():
                output_file.unlink()

    def test_write_epub_different_languages(self):
        """测试不同语言的EPUB写入"""
        chapter = Chapter(title="Test Chapter", content="<p>Test content</p>", content_type="chapter")
        volume = Volume(title="Test Volume", chapters=[chapter])

        output_file = Path(tempfile.mktemp(suffix=".epub"))

        try:
            self.writer.write_epub(
                volumes=[volume], output=output_file, title="Test Novel", author="Test Author", language="en"
            )

            assert output_file.exists()

        finally:
            if output_file.exists():
                output_file.unlink()

    def test_get_image_mime_type(self):
        """测试MIME类型获取"""
        # 测试各种扩展名
        test_cases = [
            (".jpg", "image/jpeg"),
            (".jpeg", "image/jpeg"),
            (".png", "image/png"),
            (".gif", "image/gif"),
            (".webp", "image/webp"),
            (".unknown", "image/jpeg"),  # 默认值
        ]

        for ext, expected in test_cases:
            result = self.writer._get_image_mime_type(ext)
            assert result == expected

    def test_add_cover_with_image(self):
        """测试添加封面图片"""

        # 创建空的book对象用于测试
        book = epub.EpubBook()

        # 创建临时图片文件
        cover_file = Path(tempfile.mktemp(suffix=".jpg"))
        cover_file.write_bytes(b"fake jpg data")

        try:
            # 调用_add_cover方法
            self.writer._add_cover(book, cover_file)

            # 检查book是否添加了封面相关项
            items = list(book.get_items())
            image_items = [item for item in items if isinstance(item, epub.EpubImage)]
            html_items = [item for item in items if isinstance(item, epub.EpubHtml) and "cover" in item.file_name]

            assert len(image_items) == 1
            assert len(html_items) == 1

        finally:
            if cover_file.exists():
                cover_file.unlink()

    def test_add_cover_nonexistent_image(self):
        """测试添加不存在的封面图片"""

        book = epub.EpubBook()
        nonexistent_cover = Path("nonexistent.jpg")

        # 应该不会抛出异常，而是打印警告
        self.writer._add_cover(book, nonexistent_cover)

        # 检查没有添加任何项
        items = book.get_items()
        image_items = [item for item in items if isinstance(item, epub.EpubImage)]
        assert len(image_items) == 0

    def test_add_default_styles(self):
        """测试添加默认样式"""

        book = epub.EpubBook()

        # 添加一个HTML章节
        chapter = epub.EpubHtml(title="测试章节", file_name="chapter1.xhtml")
        chapter.content = "<p>测试内容</p>"
        book.add_item(chapter)

        # 调用添加样式方法
        self.writer._add_default_styles(book)

        # 检查是否添加了样式项
        items = book.get_items()
        style_items = [item for item in items if item.media_type == "text/css"]

        # 如果存在default.css文件，应该添加了样式
        css_path = self.writer.template_dir / "default.css"
        if css_path.exists():
            assert len(style_items) == 1
            # 检查HTML章节是否有样式链接
            assert "style/default.css" in chapter.content or hasattr(chapter, "links")
        else:
            # 如果没有样式文件，不应该添加样式项
            assert len(style_items) == 0
