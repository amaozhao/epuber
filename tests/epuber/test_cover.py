"""
测试封面生成器
"""

import pytest
from epuber.cover import Cover, make_cover


class TestCover:
    """测试封面生成器"""

    def setup_method(self):
        """测试前准备"""
        try:
            self.cover = Cover()
        except ImportError:
            pytest.skip("PIL不可用")

    def test_make_default(self):
        """测试生成默认封面"""
        data = self.cover.make("测试小说", "测试作者")
        assert isinstance(data, bytes)
        assert len(data) > 0
        assert data.startswith(b'\x89PNG')  # PNG文件头

    def test_make_styles(self):
        """测试生成不同样式封面"""
        styles = ["default", "elegant", "modern", "classic"]
        for style in styles:
            data = self.cover.make("测试小说", "测试作者", style)
            assert isinstance(data, bytes)
            assert data.startswith(b'\x89PNG')

    def test_invalid_style_fallback(self):
        """测试无效样式回退到默认"""
        data = self.cover.make("测试小说", "测试作者", "invalid_style")
        assert isinstance(data, bytes)
        assert data.startswith(b'\x89PNG')

    def test_convenience_function(self):
        """测试便捷函数"""
        data = make_cover("测试小说", "测试作者")
        assert isinstance(data, bytes)
        assert data.startswith(b'\x89PNG')

    def test_empty_title_author(self):
        """测试空标题和作者"""
        data = self.cover.make("", "")
        assert isinstance(data, bytes)
        assert data.startswith(b'\x89PNG')


def test_cover_availability():
    """测试封面生成器可用性检查"""
    from epuber.cover import Cover
    availability = Cover.available()
    assert isinstance(availability, bool)

