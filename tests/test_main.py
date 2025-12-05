"""
测试主入口模块
"""

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from main import app


class TestMainApp:
    """测试主应用 CLI"""

    def setup_method(self):
        """测试前准备"""
        self.runner = CliRunner()

    def test_app_help(self):
        """测试帮助信息"""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "EPUB 生成器" in result.output

    def test_generate_command_help(self):
        """测试 generate 命令帮助"""
        result = self.runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "生成 EPUB 文件" in result.output

    def test_validate_command_help(self):
        """测试 validate 命令帮助"""
        result = self.runner.invoke(app, ["validate", "--help"])
        assert result.exit_code == 0
        assert "验证 EPUB 文件格式" in result.output

    @pytest.mark.parametrize("command", [["generate"], ["validate"]])
    def test_commands_require_arguments(self, command):
        """测试命令需要必要的参数"""
        result = self.runner.invoke(app, command)
        assert result.exit_code != 0  # 应该失败因为缺少必要参数


class TestMainIntegration:
    """集成测试"""

    def setup_method(self):
        """测试前准备"""
        # 检查是否安装了ebooklib
        try:
            import ebooklib  # noqa: F401

            self.has_ebooklib = True
        except ImportError:
            self.has_ebooklib = False

        if not self.has_ebooklib:
            pytest.skip("ebooklib not available, skipping integration tests")

        self.runner = CliRunner()
        self.temp_dir = Path("temp_test_dir")
        self.temp_dir.mkdir(exist_ok=True)

        # 创建测试小说文件
        test_content = """第一章 测试章节

这是第一章的内容。

第二章 另一个章节

这是第二章的内容。
"""
        (self.temp_dir / "test_novel.txt").write_text(test_content)

    def teardown_method(self):
        """测试后清理"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_generate_epub_success(self):
        """测试成功生成 EPUB"""
        # 指定输出目录，默认会生成 test_novel.epub
        output_file = self.temp_dir / "test_novel.epub"

        result = self.runner.invoke(
            app,
            [
                "generate",
                str(self.temp_dir / "test_novel.txt"),
                "--output",
                str(self.temp_dir),  # 指定输出目录
                "--author",
                "测试作者",
            ],
        )

        assert result.exit_code == 0
        assert "EPUB 文件已生成" in result.output
        assert output_file.exists()

    def test_validate_epub_success(self):
        """测试验证 EPUB 成功"""
        # 先创建一个 EPUB 文件用于测试
        output_file = self.temp_dir / "test_novel.epub"
        result = self.runner.invoke(
            app,
            [
                "generate",
                str(self.temp_dir / "test_novel.txt"),
                "--output",
                str(self.temp_dir),  # 指定输出目录
                "--author",
                "测试作者",
            ],
        )
        assert result.exit_code == 0

        # 现在验证它
        result = self.runner.invoke(app, ["validate", str(output_file)])
        assert result.exit_code == 0
        assert "EPUB 文件格式有效" in result.output

    def test_generate_with_default_author(self):
        """测试使用默认作者生成EPUB"""
        output_file = self.temp_dir / "test_novel.epub"

        result = self.runner.invoke(
            app,
            [
                "generate",
                str(self.temp_dir / "test_novel.txt"),
                "--output",
                str(self.temp_dir),  # 指定输出目录
                # 不指定--author，使用默认值
            ],
        )

        assert result.exit_code == 0
        assert "EPUB 文件已生成" in result.output
        assert output_file.exists()

    def test_validate_nonexistent_file(self):
        """测试验证不存在的文件"""
        nonexistent_file = self.temp_dir / "nonexistent.epub"
        result = self.runner.invoke(app, ["validate", str(nonexistent_file)])
        assert result.exit_code != 0
        assert "无效" in result.output
