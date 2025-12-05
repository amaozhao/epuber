"""
测试数据模型模块
"""

import pytest

from epuber.schemas import Chapter, Volume, EpubMetadata, EpubConfig


class TestSchemas:
    """测试数据模型"""

    def test_chapter_creation(self):
        """测试章节创建"""
        chapter = Chapter(
            title="测试章节",
            content="测试内容",
            content_type="chapter"
        )

        assert chapter.title == "测试章节"
        assert chapter.content == "测试内容"
        assert chapter.content_type == "chapter"
        assert chapter.order is None

    def test_chapter_with_order(self):
        """测试带顺序的章节"""
        chapter = Chapter(
            title="测试章节",
            content="测试内容",
            content_type="chapter",
            order=1
        )

        assert chapter.order == 1

    def test_chapter_default_content_type(self):
        """测试章节默认内容类型"""
        chapter = Chapter(
            title="测试章节",
            content="测试内容"
        )

        assert chapter.content_type == "chapter"

    def test_volume_creation(self):
        """测试卷创建"""
        chapter1 = Chapter(title="章节1", content="内容1")
        chapter2 = Chapter(title="章节2", content="内容2")

        volume = Volume(
            title="测试卷",
            chapters=[chapter1, chapter2]
        )

        assert volume.title == "测试卷"
        assert len(volume.chapters) == 2
        assert volume.chapters[0].title == "章节1"
        assert volume.order is None

    def test_volume_empty_chapters(self):
        """测试空章节卷"""
        volume = Volume(title="空卷")

        assert volume.title == "空卷"
        assert volume.chapters == []

    def test_volume_with_order(self):
        """测试带顺序的卷"""
        volume = Volume(
            title="测试卷",
            chapters=[],
            order=1
        )

        assert volume.order == 1

    def test_epub_metadata_creation(self):
        """测试EPUB元数据创建"""
        metadata = EpubMetadata(
            title="测试小说",
            author="测试作者",
            language="zh-CN"
        )

        assert metadata.title == "测试小说"
        assert metadata.author == "测试作者"
        assert metadata.language == "zh-CN"
        assert metadata.identifier is None
        assert metadata.description is None
        assert metadata.publisher is None
        assert metadata.date is None
        assert metadata.rights is None

    def test_epub_metadata_full(self):
        """测试完整的EPUB元数据"""
        metadata = EpubMetadata(
            title="测试小说",
            author="测试作者",
            language="zh-CN",
            identifier="test-id-123",
            description="测试描述",
            publisher="测试出版社",
            date="2024-01-01",
            rights="测试版权"
        )

        assert metadata.identifier == "test-id-123"
        assert metadata.description == "测试描述"
        assert metadata.publisher == "测试出版社"
        assert metadata.date == "2024-01-01"
        assert metadata.rights == "测试版权"

    def test_epub_config_creation(self):
        """测试EPUB配置创建"""
        metadata = EpubMetadata(title="测试", author="作者")
        volume = Volume(title="卷1")

        config = EpubConfig(
            metadata=metadata,
            volumes=[volume],
            output_format="epub"
        )

        assert config.metadata.title == "测试"
        assert len(config.volumes) == 1
        assert config.output_format == "epub"
        assert config.cover_image is None
        assert config.css_template is None

    def test_epub_config_with_optional(self):
        """测试带可选参数的EPUB配置"""
        metadata = EpubMetadata(title="测试", author="作者")

        config = EpubConfig(
            metadata=metadata,
            volumes=[],
            cover_image="cover.jpg",
            css_template="style.css",
            output_format="epub"
        )

        assert config.cover_image == "cover.jpg"
        assert config.css_template == "style.css"

    def test_chapter_content_types(self):
        """测试不同内容类型的章节"""
        content_types = ["chapter", "extra", "postscript", "notice"]

        for ct in content_types:
            chapter = Chapter(
                title=f"{ct}章节",
                content=f"{ct}内容",
                content_type=ct
            )
            assert chapter.content_type == ct

    def test_volume_nested_structure(self):
        """测试嵌套的卷结构"""
        # 创建子章节
        sub_chapter1 = Chapter(title="子章节1", content="内容1")
        sub_chapter2 = Chapter(title="子章节2", content="内容2")

        # 创建卷
        volume = Volume(
            title="主卷",
            chapters=[sub_chapter1, sub_chapter2]
        )

        # 创建上级结构
        root_volume = Volume(
            title="根卷",
            chapters=[volume.chapters[0]]  # 只包含第一个子章节
        )

        assert root_volume.title == "根卷"
        assert len(root_volume.chapters) == 1
        assert root_volume.chapters[0].title == "子章节1"

    def test_schema_validation(self):
        """测试数据验证"""
        # 测试必填字段
        with pytest.raises(Exception):  # Pydantic会验证必填字段
            Chapter()  # 缺少title和content

        with pytest.raises(Exception):
            Chapter(title="测试")  # 缺少content

        # 测试有效创建
        chapter = Chapter(title="测试", content="内容")
        assert chapter.title == "测试"
        assert chapter.content == "内容"

    def test_schema_field_types(self):
        """测试字段类型"""
        chapter = Chapter(
            title="测试",
            content="内容",
            content_type="chapter",
            order=1
        )

        assert isinstance(chapter.title, str)
        assert isinstance(chapter.content, str)
        assert isinstance(chapter.content_type, str)
        assert isinstance(chapter.order, int)

    def test_schema_default_values(self):
        """测试默认值"""
        chapter = Chapter(title="测试", content="内容")
        volume = Volume(title="测试卷")

        assert chapter.content_type == "chapter"
        assert chapter.order is None
        assert volume.chapters == []
        assert volume.order is None
