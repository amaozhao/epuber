"""
Epuber - EPUB 生成器包
"""

__version__ = "0.1.0"

# 导入所有模块
from .generator import EpubGenerator
from .logging import Logger, get_logger, setup_logger
from .parser import Parser
from .processor import TextProcessor
from .cover import Cover, make_cover
from .schemas import Volume, Chapter

# 可选导入（如果依赖不可用）
try:
    from .writer import Writer
except ImportError:
    Writer = None

__all__ = ["EpubGenerator", "Volume", "Chapter", "Parser", "TextProcessor", "Writer", "Cover", "make_cover", "Logger", "get_logger", "setup_logger"]
