"""
Epuber 解析器模块
负责解析单个小说文件，提取结构化数据

支持两种解析模式：
1. 无卷模式：所有章节直接作为第一层级
2. 有卷模式：卷作为第一层级，章节归属于卷

正则表达式可自定义，提供默认配置
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import chardet
from tqdm import tqdm

from .exceptions import FileParseError
from .schemas import Chapter, Volume


class Parser:
    """小说文件解析器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化解析器

        Args:
            config: 自定义配置，包含正则表达式等
        """
        self.config = self._get_default_config()
        if config:
            self.config.update(config)

    def _get_default_config(self) -> Dict[str, Any]:
        """【修改】获取默认配置：添加标题清洗正则"""
        return {
            # 卷标题正则表达式
            "volume_patterns": [
                r"^第?[一二三四五六七八九十百千万0-9]+[卷部册集]",
                r"^[上下前后]卷",
                r"^番外卷",
                r"^外传卷",
                r"^特别卷",
                r"^总集卷",
            ],
            # 章节标题正则表达式
            "chapter_patterns": [
                r"^第?[一二三四五六七八九十百千万0-9]+[章节节回话]",
                r"^序[章]",
                r"^终[章]",
                r"^尾声",
                r"^楔子",
                r"^引子",
                r"^前言",
                r"^后记",
                r"^番外[:：]",
                r"^外传[:：]",
                # 匹配：行首数字 + 点 + 1到30个字的标题内容 + 行尾 (长度为 {1,30}，未修改)
                r"^\s*[0-9]+\s*[.．、].{1,30}$",
            ],
            # 【新增】标题清洗规则
            "title_clean_patterns": [
                # 匹配中文括号及其内容
                r"【.*?】",
                r"『.*?』",
                r"〔.*?〕",
                r"（.*?）",
                # 匹配英文括号及其内容
                r"\s*\(.*?\)\s*",
                r"\s*\[.*?\]\s*",
            ],
            # 内容类型关键词
            "content_keywords": {
                "extra": ["番外", "外传", "特别篇", "番外篇", "楔子"],
                "postscript": ["后记", "尾声", "作者的话", "结束语"],
                "notice": ["公告", "声明", "更新说明", "作者声明"],
            },
            # 排除模式正则表达式（优先级最高，用于过滤误判标题）
            "exclude_patterns": [
                r"^版权声明",
                r"^版权所有",
                r"^本书版权",
                r"^著作权",
                r"^版权信息",
                r"^免责声明",
                r"^声明",
                r"^更新时间",
                r"^最后更新",
                r"^本书由",
                r"^本书来自",
                r"^内容简介",
                r"^书籍简介",
                r"^作者简介",
                r"^目录",
                r"^目\s*录",
                r"^\s*第\s*[一二三四五六七八九十百千万0-9]+\s*页",  # 页码
                r"^\s*[0-9]+\s*/\s*[0-9]+",  # 分页标记如 1/100
            ],
            # 特殊单字匹配
            "single_word_types": {
                "后记": "postscript",
                "尾声": "postscript",
                "楔子": "extra",
                "番外": "extra",
            },
        }

    def _clean_title(self, title: str) -> str:
        """【新增】清洗标题，只移除干扰信息，保留原有标题结构和数字"""

        # 1. 移除配置中定义的干扰模式（现在是通用括号）
        cleaned_title = title.strip()
        for pattern in self.config.get("title_clean_patterns", []):
            # 使用 re.sub 替换匹配到的模式为空字符串
            cleaned_title = re.sub(pattern, "", cleaned_title)

        # 2. 保证不进行任何去除数字和分隔符的操作
        return cleaned_title.strip()

    def parse(self, file_path: Path, show_progress: bool = False) -> List[Volume]:
        """解析小说文件

        Args:
            file_path: 小说文件路径

        Returns:
            结构化的卷列表
        """
        try:
            # 读取文件内容，支持多种字符集
            content = self._read_file_content(file_path)

            # 分割章节
            chapters = self._split_chapters(content, show_progress=show_progress)

            # 根据是否有卷采用不同策略
            if self._has_volumes(chapters):
                return self._create_volume_structure(chapters)
            else:
                return self._create_flat_structure(chapters)

        except FileParseError:
            # 重新抛出FileParseError，不包装
            raise
        except Exception as e:
            raise FileParseError(f"解析文件失败: {file_path}") from e

    def _read_file_content(self, file_path: Path) -> str:
        """读取文件内容，支持多种字符集自动检测

        Args:
            file_path: 文件路径

        Returns:
            解码后的文本内容

        Raises:
            FileParseError: 当所有编码都无法解码时
        """

        with open(file_path, "rb") as f:
            raw_data = f.read()

        # 使用chardet检测字符集
        detected = chardet.detect(raw_data)
        confidence = detected.get("confidence", 0)
        encoding = detected.get("encoding")

        # 如果检测到编码且置信度足够高
        if encoding and confidence > 0.7:
            try:
                # 特殊处理UTF-8 BOM
                if raw_data.startswith(b"\xef\xbb\xbf") and encoding.lower() == "utf-8":
                    return raw_data.decode("utf-8-sig")
                else:
                    return raw_data.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                pass

        # Fallback: 尝试常见中文编码
        fallback_encodings = ["utf-8", "gbk", "gb2312", "big5", "utf-16"]

        for enc in fallback_encodings:
            try:
                # 检查UTF-8 BOM
                if raw_data.startswith(b"\xef\xbb\xbf") and enc == "utf-8":
                    return raw_data.decode("utf-8-sig")
                else:
                    return raw_data.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue

        # 最后的fallback：使用错误替换
        try:
            return raw_data.decode("utf-8", errors="replace")
        except Exception:
            raise FileParseError(f"无法解码文件内容: {file_path}。文件可能已损坏或使用了不支持的编码。")

    def _split_chapters(self, content: str, show_progress: bool = False) -> List[Dict[str, Any]]:
        """【修改】将小说内容按章节分割，并对标题进行清洗"""
        lines = content.split("\n")
        iterator = tqdm(lines, desc="解析章节", unit="行", disable=not show_progress) if show_progress else lines
        chapters = []
        current_title = None
        current_content = []

        for line in iterator:
            line_stripped = line.strip()

            # 按照优先级顺序检查：排除模式 -> 一级目录模式 -> 二级目录模式
            # 如果是排除行，则跳过，不作为标题处理
            # 注意：检测方法现在期望原始行内容（包含可能的行首空白）
            if not self._is_exclude_line(line) and (self._is_volume_title(line) or self._is_chapter_title(line)):
                # 保存之前的章节
                if current_title is not None:
                    chapter_data = self._create_chapter_data(
                        title=current_title, content="\n".join(current_content).strip()
                    )
                    if chapter_data["content"]:  # 只添加有内容的章节
                        chapters.append(chapter_data)

                # 开始新章节
                current_title = self._clean_title(line_stripped)

                # 如果清洗后标题为空，保留原行，避免流程被改变
                if not current_title:
                    current_content.append(line)
                    current_title = None
                    continue

                current_content = []
            else:
                # 累积内容
                current_content.append(line)

        # 添加最后一个章节
        if current_title is not None:
            chapter_data = self._create_chapter_data(title=current_title, content="\n".join(current_content).strip())
            if chapter_data["content"]:
                chapters.append(chapter_data)

        # 如果没有找到任何章节标题，抛出异常（设计文档要求）
        if not chapters:
            raise FileParseError("未能在文件中找到任何章节。请检查文件内容或正则表达式配置。")

        return chapters

    def _create_chapter_data(self, title: str, content: str) -> Dict[str, Any]:
        """创建章节数据"""
        # 原始逻辑，未修改
        return {
            "title": title,
            "content": content,
            "type": self._detect_content_type(title),
            "is_volume": self._is_volume_title(title),
        }

    def _is_volume_title(self, line: str) -> bool:
        """检测是否为卷标题"""
        # 标题长度限制：最长30个字符
        if len(line.strip()) > 30:
            return False

        # 标题必须从行首开始，不以空白字符开头
        if line.startswith((" ", "\t", "\n", "\r", "\v", "\f")):
            return False

        for pattern in self.config["volume_patterns"]:
            if re.search(pattern, line):
                return True
        return False

    def _is_exclude_line(self, line: str) -> bool:
        """检测是否为应排除的行（优先级最高）"""
        # 排除行也需要长度检查，避免误判过长的行
        if len(line.strip()) > 50:  # 排除行可以稍微长一些
            return False

        # 排除行必须从行首开始，不以空白字符开头
        if line.startswith((" ", "\t", "\n", "\r", "\v", "\f")):
            return False

        for pattern in self.config["exclude_patterns"]:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def _is_chapter_title(self, line: str) -> bool:
        """检测是否为章节标题"""
        # 标题长度限制：最长30个字符
        if len(line.strip()) > 30:
            return False

        # 标题必须从行首开始，不以空白字符开头
        if line.startswith((" ", "\t", "\n", "\r", "\v", "\f")):
            return False

        # 只使用正则表达式匹配，避免关键词匹配导致的误判
        for pattern in self.config["chapter_patterns"]:
            if re.search(pattern, line):
                return True

        return False

    def _detect_content_type(self, title: str) -> str:
        """检测内容类型"""
        title_lower = title.lower()

        # 检查关键词
        for content_type, keywords in self.config["content_keywords"].items():
            if any(keyword.lower() in title_lower for keyword in keywords):
                return content_type

        # 检查特殊单字
        for word, content_type in self.config["single_word_types"].items():
            if word in title:
                return content_type

        return "chapter"

    def _has_volumes(self, chapters: List[Dict[str, Any]]) -> bool:
        """检查是否有卷标题"""
        # 原始逻辑，未修改
        return any(chapter["is_volume"] for chapter in chapters)

    def _create_flat_structure(self, chapters: List[Dict[str, Any]]) -> List[Volume]:
        """创建扁平结构（无卷时）"""
        volumes = []

        for chapter_data in chapters:
            chapter = Chapter(
                title=chapter_data["title"], content=chapter_data["content"], content_type=chapter_data["type"]
            )

            # 每个章节都作为独立的Volume（第一层级）
            volume = Volume(title=chapter.title, chapters=[chapter])
            volumes.append(volume)

        return volumes

    def _create_volume_structure(self, chapters: List[Dict[str, Any]]) -> List[Volume]:
        """创建卷结构（有卷时）"""
        volumes = []
        current_volume = None

        for chapter_data in chapters:
            if chapter_data["is_volume"]:
                # 创建新卷
                current_volume = Volume(title=chapter_data["title"], chapters=[])
                volumes.append(current_volume)

                # 将卷标题作为章节添加到卷中
                volume_chapter = Chapter(
                    title=chapter_data["title"], content=chapter_data["content"], content_type="chapter"
                )
                current_volume.chapters.append(volume_chapter)

            elif chapter_data["type"] in ["extra", "postscript", "notice"]:
                # 特殊内容直接作为第一层级
                special_chapter = Chapter(
                    title=chapter_data["title"], content=chapter_data["content"], content_type=chapter_data["type"]
                )
                special_volume = Volume(title=chapter_data["title"], chapters=[special_chapter])
                volumes.append(special_volume)

            else:
                # 普通章节归入当前卷
                if current_volume is not None:
                    regular_chapter = Chapter(
                        title=chapter_data["title"], content=chapter_data["content"], content_type=chapter_data["type"]
                    )
                    current_volume.chapters.append(regular_chapter)

        return volumes

    def _has_volumes(self, chapters: List[Dict[str, Any]]) -> bool:
        """检查是否有卷标题"""
        for chapter_data in chapters:
            if chapter_data["is_volume"]:
                return True
        return False

    def _create_flat_structure(self, chapters: List[Dict[str, Any]]) -> List[Volume]:
        """创建扁平结构（无卷时，所有章节作为第一层级内容）"""
        # 创建一个大的"内容"容器，包含所有章节
        all_chapters = []
        for chapter_data in chapters:
            chapter = Chapter(
                title=chapter_data["title"], content=chapter_data["content"], content_type=chapter_data["type"]
            )
            all_chapters.append(chapter)

        # 返回一个包含所有章节的Volume，标题为None表示这是内容容器
        return [Volume(title=None, chapters=all_chapters)]
