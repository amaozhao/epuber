"""
Epuber - EPUB 生成器主入口
"""

import re
import traceback
from pathlib import Path

import typer

from epuber.generator import EpubGenerator
from epuber.logging import setup_logger

app = typer.Typer(help="EPUB 生成器 - 将小说文本转换为 EPUB 格式")


@app.command()
def generate(
    input: Path = typer.Argument(..., help="输入小说文件路径"),
    output: Path = typer.Option(None, "-o", "--output", help="输出目录，默认为输入文件所在目录"),
    author: str = typer.Option("AmaoZhao", help="作者姓名"),
    language: str = typer.Option("zh-CN", help="语言代码"),
    cover: Path = typer.Option(None, help="封面图片路径"),
    cover_style: str = typer.Option("default", help="自动封面样式 (default/elegant/modern/classic)"),
    volume_regex: str = typer.Option(None, help="自定义卷标题正则表达式"),
    chapter_regex: str = typer.Option(None, help="自定义章节标题正则表达式"),
    exclude_regex: str = typer.Option(None, help="自定义排除模式正则表达式"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="启用详细日志输出"),
):
    """
    生成 EPUB 文件
    """
    # 设置日志
    logger = setup_logger(verbose)

    try:
        logger.step(1, "初始化 EPUB 生成器")

        # 构建解析器配置
        parser_config = {}

        # 验证并设置卷标题正则表达式
        if volume_regex:
            try:
                re.compile(volume_regex)
                parser_config["volume_patterns"] = [volume_regex]
                logger.debug(f"使用自定义卷标题正则表达式: {volume_regex}")
            except re.error as e:
                logger.failure(f"卷标题正则表达式语法错误: {e}")
                raise typer.Exit(1)

        # 验证并设置章节标题正则表达式
        if chapter_regex:
            try:
                re.compile(chapter_regex)
                parser_config["chapter_patterns"] = [chapter_regex]
                logger.debug(f"使用自定义章节标题正则表达式: {chapter_regex}")
            except re.error as e:
                logger.failure(f"章节标题正则表达式语法错误: {e}")
                raise typer.Exit(1)

        # 验证并设置排除模式正则表达式
        if exclude_regex:
            try:
                re.compile(exclude_regex)
                parser_config["exclude_patterns"] = [exclude_regex]
                logger.debug(f"使用自定义排除模式正则表达式: {exclude_regex}")
            except re.error as e:
                logger.failure(f"排除模式正则表达式语法错误: {e}")
                raise typer.Exit(1)

        generator = EpubGenerator()

        # 确定输出目录
        if output is None:
            output = input.parent

        # 验证输出目录
        try:
            output.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.failure(f"无法创建输出目录 '{output}': {e}")
            raise typer.Exit(1)

        # 检查输出目录是否可写
        try:
            test_file = output / ".epuber_write_test"
            test_file.write_text("test")
            test_file.unlink()
        except (OSError, PermissionError) as e:
            logger.failure(f"输出目录 '{output}' 不可写: {e}")
            raise typer.Exit(1)

        # 生成输出文件路径
        output_filename = input.stem + ".epub"
        output_path = output / output_filename

        # 从输入文件名提取标题
        title = input.stem
        logger.debug(f"使用输入文件名作为标题: {title}")

        logger.step(2, f"开始生成 EPUB: {title}")
        logger.debug(f"输出路径: {output_path}")

        generator.generate_epub(
            input=input,
            output=output_path,
            title=title,
            author=author,
            language=language,
            cover=cover,
            cover_style=cover_style,
            logger=logger,
            parser_config=parser_config if parser_config else None,
        )

        logger.success(f"EPUB 文件已生成: {output_path}")

    except Exception as e:
        logger.failure(f"生成失败: {e}")
        # 在verbose模式下显示完整的错误回溯
        if verbose:
            logger.logger.error("完整错误信息:")
            logger.logger.error(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def validate(
    input: Path = typer.Argument(..., help="要验证的 EPUB 文件"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="启用详细日志输出"),
):
    """
    验证 EPUB 文件格式
    """
    # 设置日志
    logger = setup_logger(verbose)

    try:
        logger.step(1, f"开始验证 EPUB 文件: {input}")
        generator = EpubGenerator()
        is_valid = generator.validate_epub(input)

        if is_valid:
            logger.success("EPUB 文件格式有效")
        else:
            logger.failure("EPUB 文件格式无效")
            raise typer.Exit(1)

    except Exception as e:
        logger.failure(f"验证失败: {e}")
        # 在verbose模式下显示完整的错误回溯
        if verbose:
            logger.logger.error("完整错误信息:")
            logger.logger.error(traceback.format_exc())
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
