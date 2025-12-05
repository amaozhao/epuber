"""
测试解析器模块
"""

import os
import tempfile
from pathlib import Path

import pytest

from epuber.exceptions import FileParseError
from epuber.parser import Parser
from epuber.schemas import Chapter, Volume


class TestParser:
    """测试 Parser 类"""

    def setup_method(self):
        """测试前准备"""
        self.parser = Parser()

    def teardown_method(self):
        """测试后清理"""
        pass

    def test_init_default_config(self):
        """测试默认配置初始化"""
        parser = Parser()
        assert "volume_patterns" in parser.config
        assert "chapter_patterns" in parser.config
        assert "content_keywords" in parser.config
        assert len(parser.config["volume_patterns"]) > 0
        assert len(parser.config["chapter_patterns"]) > 0

    def test_init_custom_config(self):
        """测试自定义配置初始化"""
        custom_config = {
            "volume_patterns": [r"^VOL\d+"],
            "chapter_patterns": [r"^CH\d+"],
            "content_keywords": {"extra": ["EXTRA"]},
        }
        parser = Parser(custom_config)
        assert parser.config["volume_patterns"] == [r"^VOL\d+"]
        assert parser.config["chapter_patterns"] == [r"^CH\d+"]
        assert parser.config["content_keywords"]["extra"] == ["EXTRA"]

    def test_parse_with_volumes(self):
        """测试有卷标题的解析"""
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
            temp_file = f.name

        try:
            volumes = self.parser.parse(Path(temp_file))

            # 应该有3个卷：第一卷（包含卷标题+2章）、番外、后记
            assert len(volumes) == 3

            # 检查第一卷
            vol1 = volumes[0]
            assert vol1.title == "第一卷 相遇"
            assert len(vol1.chapters) == 3
            assert vol1.chapters[0].title == "第一卷 相遇"
            assert vol1.chapters[1].title == "第1章 初遇"
            assert vol1.chapters[2].title == "第2章 发展"

            # 检查番外
            extra_vol = next(v for v in volumes if "番外" in v.title)
            assert len(extra_vol.chapters) == 1
            assert extra_vol.chapters[0].content_type == "extra"

            # 检查后记
            postscript_vol = next(v for v in volumes if "后记" in v.title)
            assert len(postscript_vol.chapters) == 1
            assert postscript_vol.chapters[0].content_type == "postscript"

        finally:
            os.unlink(temp_file)

    def test_parse_without_volumes(self):
        """测试无卷标题的解析（扁平结构）"""
        content = """第1章 开始

故事开始...

第2章 发展

继续发展...

番外：额外

额外内容...

后记

感谢读者支持...
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            volumes = self.parser.parse(Path(temp_file))

            # 应该有1个卷，包含所有章节作为第一层级
            assert len(volumes) == 1
            assert volumes[0].title is None

            # 卷中有4个章节
            assert len(volumes[0].chapters) == 4

            chapter_titles = [c.title for c in volumes[0].chapters]
            assert "第1章 开始" in chapter_titles
            assert "第2章 发展" in chapter_titles
            assert "番外：额外" in chapter_titles
            assert "后记" in chapter_titles

            # 检查内容类型
            postscript_chapter = next(c for c in volumes[0].chapters if "后记" in c.title)
            assert postscript_chapter.content_type == "postscript"

        finally:
            os.unlink(temp_file)

    def test_parse_custom_config(self):
        """测试自定义配置解析"""
        custom_config = {
            "volume_patterns": [r"^VOL\d+"],
            "chapter_patterns": [r"^CH\d+", r"^EXTRA", r"^ENDING"],
            "content_keywords": {"extra": ["EXTRA"], "postscript": ["ENDING"]},
        }
        parser = Parser(custom_config)

        content = """VOL1 Start

Begin...

CH1 Meet

They meet...

EXTRA

Side story...

ENDING

The end...
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            volumes = parser.parse(Path(temp_file))

            # 应该有3个卷：VOL1（包含VOL1+CH1）、EXTRA、ENDING
            assert len(volumes) == 3

            vol1 = next(v for v in volumes if "VOL1" in v.title)
            assert len(vol1.chapters) == 2  # VOL1 + CH1
            assert vol1.chapters[0].title == "VOL1 Start"
            assert vol1.chapters[1].title == "CH1 Meet"

            extra_vol = next(v for v in volumes if "EXTRA" in v.title)
            assert len(extra_vol.chapters) == 1
            assert extra_vol.chapters[0].content_type == "extra"

        finally:
            os.unlink(temp_file)

    def test_split_chapters(self):
        """测试章节分割功能"""
        content = """第一卷 相遇

这是一个卷的开始。

第1章 初遇

小明和小红相遇了。

第2章 发展

他们的关系开始发展。

番外：回忆

这是番外的故事。

后记

感谢读者支持。
"""

        chapters = self.parser._split_chapters(content)

        assert len(chapters) == 5
        assert chapters[0]["title"] == "第一卷 相遇"
        assert chapters[0]["is_volume"]
        assert chapters[1]["title"] == "第1章 初遇"
        assert not chapters[1]["is_volume"]
        assert chapters[2]["title"] == "第2章 发展"
        assert chapters[3]["title"] == "番外：回忆"
        assert chapters[4]["title"] == "后记"

    def test_is_volume_title(self):
        """测试卷标题识别"""
        assert self.parser._is_volume_title("第一卷 相遇")
        assert self.parser._is_volume_title("第2部 发展")
        assert self.parser._is_volume_title("上卷")
        assert not self.parser._is_volume_title("第1章 初遇")
        assert not self.parser._is_volume_title("普通内容")

    def test_is_chapter_title(self):
        """测试章节标题识别"""
        assert self.parser._is_chapter_title("第1章 初遇")
        assert self.parser._is_chapter_title("番外：回忆")
        assert self.parser._is_chapter_title("后记")
        assert not self.parser._is_chapter_title("第一卷 相遇")  # 卷标题不应该是章节标题
        assert not self.parser._is_chapter_title("普通内容行")

    def test_is_exclude_line(self):
        """测试排除行识别"""
        # 应该被排除的行
        assert self.parser._is_exclude_line("版权声明：本书版权归作者所有")
        assert self.parser._is_exclude_line("免责声明：本书内容纯属虚构")
        assert self.parser._is_exclude_line("最后更新时间：2024-01-01")
        assert self.parser._is_exclude_line("本书由某某平台提供")
        assert self.parser._is_exclude_line("著作权声明")
        assert self.parser._is_exclude_line("第 5 页")
        assert self.parser._is_exclude_line("10/100")

        # 不应该被排除的行（正常章节标题）
        assert not self.parser._is_exclude_line("第一章 开始冒险")
        assert not self.parser._is_exclude_line("第二章 遇到困难")
        assert not self.parser._is_exclude_line("番外：回忆")
        assert not self.parser._is_exclude_line("普通内容行")

    def test_detect_content_type(self):
        """测试内容类型检测"""
        assert self.parser._detect_content_type("第1章 初遇") == "chapter"
        assert self.parser._detect_content_type("番外：回忆") == "extra"
        assert self.parser._detect_content_type("后记") == "postscript"
        assert self.parser._detect_content_type("公告：更新") == "notice"

    def test_has_volumes(self):
        """测试卷检测"""
        chapters_with_volumes = [
            {"title": "第一卷 相遇", "is_volume": True},
            {"title": "第1章 初遇", "is_volume": False},
        ]
        chapters_without_volumes = [
            {"title": "第1章 初遇", "is_volume": False},
            {"title": "第2章 发展", "is_volume": False},
        ]

        assert self.parser._has_volumes(chapters_with_volumes)
        assert not self.parser._has_volumes(chapters_without_volumes)

    def test_create_flat_structure(self):
        """测试扁平结构创建"""
        chapters = [
            {"title": "第1章 初遇", "content": "内容1", "type": "chapter", "is_volume": False},
            {"title": "番外：回忆", "content": "内容2", "type": "extra", "is_volume": False},
        ]

        volumes = self.parser._create_flat_structure(chapters)

        # 应该返回1个卷，包含所有章节
        assert len(volumes) == 1
        assert volumes[0].title is None
        assert len(volumes[0].chapters) == 2

        # 检查章节内容
        chapter_titles = [c.title for c in volumes[0].chapters]
        assert "第1章 初遇" in chapter_titles
        assert "番外：回忆" in chapter_titles

        content_types = [c.content_type for c in volumes[0].chapters]
        assert "chapter" in content_types
        assert "extra" in content_types

    def test_create_volume_structure(self):
        """测试卷结构创建"""
        chapters = [
            {"title": "第一卷 相遇", "content": "卷内容", "type": "chapter", "is_volume": True},
            {"title": "第1章 初遇", "content": "章内容1", "type": "chapter", "is_volume": False},
            {"title": "第2章 发展", "content": "章内容2", "type": "chapter", "is_volume": False},
            {"title": "番外：回忆", "content": "番外内容", "type": "extra", "is_volume": False},
        ]

        volumes = self.parser._create_volume_structure(chapters)

        # 应该有2个卷：第一卷（3章）、番外（1章）
        assert len(volumes) == 2

        vol1 = volumes[0]
        assert vol1.title == "第一卷 相遇"
        assert len(vol1.chapters) == 3
        assert vol1.chapters[0].title == "第一卷 相遇"
        assert vol1.chapters[1].title == "第1章 初遇"
        assert vol1.chapters[2].title == "第2章 发展"

        extra_vol = volumes[1]
        assert "番外" in extra_vol.title
        assert len(extra_vol.chapters) == 1
        assert extra_vol.chapters[0].content_type == "extra"

    def test_parse_file_not_found(self):
        """测试文件不存在的情况"""
        with pytest.raises(FileParseError):
            self.parser.parse(Path("nonexistent_file.txt"))

    def test_parse_empty_file(self):
        """测试空文件"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write("")  # 空文件
            temp_file = f.name

        try:
            # 空文件应该抛出异常（设计文档要求）
            with pytest.raises(FileParseError, match="未能在文件中找到任何章节"):
                self.parser.parse(Path(temp_file))
        finally:
            os.unlink(temp_file)

    def test_parse_with_exclude_lines(self):
        """测试解析包含排除行的文件"""
        content = """版权声明：本书版权归作者所有，未经许可不得转载。

免责声明：本书内容纯属虚构。

第一章 开始冒险

这是一个精彩的故事开始。
故事的第一段内容。

最后更新时间：2024-01-01

第二章 遇到困难

故事继续发展。
遇到了一些困难。

本书由某某平台提供。

第三章 解决难题

问题终于解决了。
故事圆满结束。
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            volumes = self.parser.parse(Path(temp_path))

            # 应该有1个卷，包含所有有效章节
            assert len(volumes) == 1
            assert volumes[0].title is None
            assert len(volumes[0].chapters) == 3

            # 验证章节标题
            chapter_titles = [chapter.title for chapter in volumes[0].chapters]
            assert "第一章 开始冒险" in chapter_titles
            assert "第二章 遇到困难" in chapter_titles
            assert "第三章 解决难题" in chapter_titles

            # 验证没有版权声明等被当作章节标题
            for title in chapter_titles:
                assert not title.startswith("版权声明")
                assert not title.startswith("免责声明")
                assert not title.startswith("最后更新时间")
                assert not title.startswith("本书由")

        finally:
            os.unlink(temp_path)

    def test_read_file_content_utf8(self):
        """测试UTF-8文件读取"""
        content = "第1章 测试\n这是UTF-8内容"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            result = self.parser._read_file_content(Path(temp_file))
            assert result == content
        finally:
            os.unlink(temp_file)

    def test_read_file_content_utf8_with_bom(self):
        """测试带BOM的UTF-8文件读取"""
        content = "第1章 测试\n这是带BOM的UTF-8内容"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8-sig", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            result = self.parser._read_file_content(Path(temp_file))
            assert result == content
        finally:
            os.unlink(temp_file)

    def test_read_file_content_gbk(self):
        """测试GBK编码文件读取"""
        content = "第1章 测试\n这是GBK编码内容"
        # 创建GBK编码的文件
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            f.write(content.encode("gbk"))
            temp_file = f.name

        try:
            result = self.parser._read_file_content(Path(temp_file))
            assert result == content
        finally:
            os.unlink(temp_file)

    def test_read_file_content_big5(self):
        """测试Big5编码文件读取"""
        content = "第1章 測試\n這是Big5編碼內容"
        # 创建Big5编码的文件
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            f.write(content.encode("big5"))
            temp_file = f.name

        try:
            result = self.parser._read_file_content(Path(temp_file))
            assert result == content
        finally:
            os.unlink(temp_file)

    def test_read_file_content_corrupted(self):
        """测试损坏文件的情况"""
        # 创建包含无效UTF-8序列的文件
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            # 写入一些无效的字节序列
            f.write(b"\xff\xfe\x00\x00\x01\x00\x00\x00")
            temp_file = f.name

        try:
            # 应该能够用错误替换的方式读取
            result = self.parser._read_file_content(Path(temp_file))
            assert isinstance(result, str)
            assert len(result) > 0
        finally:
            os.unlink(temp_file)


class TestSchemas:
    """测试数据模型"""

    def test_chapter_creation(self):
        """测试章节创建"""
        chapter = Chapter(title="测试章节", content="测试内容")

        assert chapter.title == "测试章节"
        assert chapter.content == "测试内容"
        assert chapter.order is None

    def test_volume_creation(self):
        """测试卷创建"""
        chapter1 = Chapter(title="章节1", content="内容1")
        chapter2 = Chapter(title="章节2", content="内容2")

        volume = Volume(title="测试卷", chapters=[chapter1, chapter2])

        assert volume.title == "测试卷"
        assert len(volume.chapters) == 2
        assert volume.chapters[0].title == "章节1"

    def test_volume_empty_chapters(self):
        """测试空章节卷"""
        volume = Volume(title="空卷")

        assert volume.title == "空卷"
        assert volume.chapters == []
