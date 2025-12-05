"""
Epuber 写入器模块
负责EPUB文件的生成和输出
"""

from pathlib import Path
from typing import List, Optional

from ebooklib import epub
from tqdm import tqdm

from .cover import Cover
from .schemas import Volume


class Writer:
    """写入器类，负责EPUB文件的生成"""

    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.cover_gen = Cover() if Cover.available() else None

    def write_epub(
        self,
        volumes: List[Volume],
        output: Path,
        title: str,
        author: str,
        language: str = "zh-CN",
        cover: Optional[Path] = None,
        cover_style: str = "default",
        show_progress: bool = False,
    ) -> None:
        """
        生成 EPUB 文件

        Args:
            volumes: 卷列表
            output: 输出文件路径
            title: 书籍标题
            author: 作者姓名
            language: 语言代码
            cover: 封面图片路径
        """
        # 创建 EPUB 书籍对象
        book = epub.EpubBook()

        # 设置基本信息
        book.set_identifier(f"epuber-{title}-{author}")
        book.set_title(title)
        book.set_language(language)

        # 添加作者信息
        book.add_author(author)

        # 创建章节
        epub_chapters = []
        toc_items = []

        total_chapters = sum(len(volume.chapters) for volume in volumes)
        chapter_pbar = tqdm(
            total=total_chapters,
            desc="写入章节",
            unit="章",
            disable=not show_progress,
        )

        for volume in volumes:
            # 为每个卷创建标题页（可选）
            if volume.title:
                volume_chapter = epub.EpubHtml(
                    title=volume.title, file_name=f"volume_{len(epub_chapters)}.xhtml", lang=language
                )
                volume_chapter.content = f"<h1>{volume.title}</h1>"
                book.add_item(volume_chapter)
                epub_chapters.append(volume_chapter)
                toc_items.append(volume_chapter)

            # 添加卷中的章节
            for chapter in volume.chapters:
                epub_chapter = epub.EpubHtml(
                    title=chapter.title, file_name=f"chapter_{len(epub_chapters)}.xhtml", lang=language
                )

                title_html = f"<h1>{chapter.title}</h1>"
                epub_chapter.content = title_html + "\n" + chapter.content

                book.add_item(epub_chapter)
                epub_chapters.append(epub_chapter)
                toc_items.append(epub_chapter)
                chapter_pbar.update(1)

        chapter_pbar.close()

        # 添加封面（返回封面页以便加入阅读顺序）
        cover_page = None
        if cover and cover.exists():
            cover_page = self._add_cover(book, cover)
        elif self.cover_gen:
            # 自动生成封面
            try:
                cover_data = self.cover_gen.make(title, author, cover_style)
                cover_page = self._add_generated_cover(book, cover_data)
            except Exception as e:
                print(f"警告: 无法生成自动封面: {e}")

        # 添加默认样式
        self._add_default_styles(book)

        # 设置目录结构
        book.toc = toc_items

        # 添加导航文件
        book.add_item(epub.EpubNcx())
        nav_file = epub.EpubNav()
        book.add_item(nav_file)

        # 立即为导航文件添加CSS链接
        if hasattr(nav_file, "add_link"):
            nav_file.add_link(href="style/default.css", rel="stylesheet", type="text/css")

        # 设置阅读顺序（优先展示封面 -> 目录 -> 正文）
        spine_items = []
        if cover_page:
            spine_items.append(cover_page)
        spine_items.append("nav")
        spine_items.extend(epub_chapters)
        book.spine = spine_items

        # 生成 EPUB 文件
        try:
            epub.write_epub(str(output), book, {})
        except PermissionError:
            raise IOError(f"权限不足，无法写入文件: {output}")
        except OSError as e:
            if hasattr(e, "errno"):
                if e.errno == 28:  # No space left on device
                    raise IOError(f"磁盘空间不足，无法生成EPUB文件: {output}")
                elif e.errno == 36:  # File name too long
                    raise IOError(f"文件路径过长: {output}")
                elif e.errno == 2:  # No such file or directory
                    raise IOError(f"输出目录不存在: {output.parent}")
            raise IOError(f"文件写入失败: {e}")

    def _add_cover(self, book: epub.EpubBook, cover_path: Path):
        """
        添加封面图片

        Args:
            book: EPUB 书籍对象
            cover_path: 封面图片路径
        """
        try:
            # 读取图片文件
            image_content = cover_path.read_bytes()

            # 创建封面图片项
            image_name = f"cover{cover_path.suffix}"
            cover_image = epub.EpubImage()
            cover_image.file_name = image_name
            cover_image.media_type = self._get_image_mime_type(cover_path.suffix)
            cover_image.content = image_content

            # 创建封面图片项
            cover_image = epub.EpubImage()
            cover_image.file_name = image_name
            cover_image.id = "cover-image"
            cover_image.media_type = self._get_image_mime_type(cover_path.suffix)
            cover_image.content = image_content
            book.add_item(cover_image)

            # 创建封面页面
            cover_page = epub.EpubHtml(title="封面", file_name="cover.xhtml")
            cover_page.id = "cover-page"
            cover_page.content = f'<img src="{image_name}" alt="封面" style="max-width: 100%; height: auto;" />'
            book.add_item(cover_page)

            # 设置封面元数据（不自动生成封面页，避免重复）
            book.add_metadata("http://www.idpf.org/2007/opf", "meta", "", {"name": "cover", "content": cover_image.id})

            return cover_page

        except Exception as e:
            print(f"警告: 无法添加封面图片: {e}")
            return None

    def _add_generated_cover(self, book: epub.EpubBook, cover_data: bytes):
        """
        添加自动生成的封面

        Args:
            book: EPUB书籍对象
            cover_data: PNG格式的封面数据
        """
        # 创建封面图片项
        cover_image = epub.EpubImage()
        cover_image.file_name = "cover.png"
        cover_image.id = "cover-image"
        cover_image.media_type = "image/png"
        cover_image.content = cover_data
        book.add_item(cover_image)

        # 创建封面页面
        cover_page = epub.EpubHtml(title="封面", file_name="cover.xhtml")
        cover_page.id = "cover-page"
        cover_page.content = '<img src="cover.png" alt="封面" style="max-width: 100%; height: auto;" />'
        book.add_item(cover_page)

        # 设置封面元数据
        book.add_metadata("http://www.idpf.org/2007/opf", "meta", "", {"name": "cover", "content": cover_image.id})

        return cover_page

    def _get_image_mime_type(self, suffix: str) -> str:
        """
        根据文件扩展名获取 MIME 类型

        Args:
            suffix: 文件扩展名

        Returns:
            MIME 类型
        """
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return mime_types.get(suffix.lower(), "image/jpeg")

    def _add_default_styles(self, book: epub.EpubBook) -> None:
        """
        添加默认样式

        Args:
            book: EPUB 书籍对象
        """
        css_path = self.template_dir / "default.css"
        if css_path.exists():
            css_content = css_path.read_text(encoding="utf-8")
            style = epub.EpubItem(
                uid="style_default", file_name="style/default.css", media_type="text/css", content=css_content
            )
            book.add_item(style)

            # 为所有HTML项目添加样式链接（包括导航文件）
            for item in book.get_items():
                if isinstance(item, epub.EpubHtml):
                    item.add_link(href="style/default.css", rel="stylesheet", type="text/css")
                # 单独处理导航文件
                elif hasattr(item, "add_link") and item.file_name and item.file_name.endswith("nav.xhtml"):
                    item.add_link(href="style/default.css", rel="stylesheet", type="text/css")
