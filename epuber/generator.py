"""
Epuber 生成器模块
EPUB 生成器协调器，负责编排各个组件
"""

from pathlib import Path
from typing import Optional

from .exceptions import EpubGenerationError
from .logging import Logger
from .parser import Parser
from .processor import TextProcessor
from tqdm import tqdm

# 可选导入writer
try:
    from .writer import Writer
except ImportError:
    Writer = None


class EpubGenerator:
    """EPUB 生成器协调器类"""

    def __init__(self):
        """初始化各个组件"""
        self.parser = Parser()
        self.processor = TextProcessor()
        self._writer = None

    @property
    def writer(self):
        """获取writer实例"""
        if self._writer is None and Writer is not None:
            self._writer = Writer()
        return self._writer

    def generate_epub(
        self,
        input: Path,
        output: Path,
        title: str,
        author: str,
        language: str = "zh-CN",
        cover: Optional[Path] = None,
        cover_style: str = "default",
        logger: Optional[Logger] = None,
        parser_config: Optional[dict] = None,
    ) -> None:
        """
        生成 EPUB 文件

        Args:
            input: 输入文件路径
            output: 输出文件路径
            title: 书籍标题
            author: 作者姓名
            language: 语言代码
            cover: 封面图片路径
            cover_style: 自动封面样式
            logger: 日志记录器
            parser_config: 解析器配置
        """
        try:
            progress_enabled = logger is not None

            # 1. 解析输入文件
            if logger:
                logger.progress_start("解析输入文件")
            parser = Parser(config=parser_config)
            volumes = parser.parse(input, show_progress=progress_enabled)
            if logger:
                logger.progress_complete(f"解析完成，发现 {len(volumes)} 个卷/章节")

            # 2. 处理文本内容
            total_chapters = sum(len(volume.chapters) for volume in volumes)
            if logger:
                logger.progress_start("处理文本内容")
            with tqdm(
                total=total_chapters,
                desc="处理章节",
                unit="章",
                disable=not progress_enabled,
            ) as pbar:
                for volume in volumes:
                    for chapter in volume.chapters:
                        chapter.content = self.processor.process_content(chapter.content)
                        pbar.update(1)
                        if logger and logger.verbose:
                            logger.debug(f"已处理章节: {chapter.title}")
            if logger:
                logger.progress_complete(f"文本处理完成，共处理 {total_chapters} 个章节")

            # 3. 检查writer是否可用
            if self.writer is None:
                raise EpubGenerationError("EPUB生成需要ebooklib库，请安装: pip install ebooklib")

            # 4. 生成 EPUB 文件
            if logger:
                logger.progress_start("生成 EPUB 文件")
            self.writer.write_epub(
                volumes=volumes,
                output=output,
                title=title,
                author=author,
                language=language,
                cover=cover,
                show_progress=progress_enabled,
            )
            if logger:
                logger.progress_complete(f"EPUB 文件生成完成: {output}")

        except Exception as e:
            if logger:
                logger.error(f"生成过程出错: {e}")
            raise EpubGenerationError(f"生成 EPUB 失败: {e}") from e

    def validate_epub(self, epub_path: Path) -> bool:
        """
        验证 EPUB 文件格式

        Args:
            epub_path: EPUB 文件路径

        Returns:
            是否有效
        """
        try:
            # 基本的文件存在性检查
            if not epub_path.exists():
                return False

            # 检查文件大小
            if epub_path.stat().st_size == 0:
                return False

            # 检查文件扩展名
            if epub_path.suffix.lower() != ".epub":
                return False

            # 这里可以添加更复杂的 EPUB 格式验证
            # 比如检查 ZIP 结构、META-INF/container.xml 等

            return True

        except Exception:
            return False
