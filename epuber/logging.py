"""
Epuber 日志模块
提供带颜色的控制台输出和详细日志功能
"""

import logging
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text


class Logger:
    """统一日志管理器"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = Console()

        # 设置标准logging
        self._setup_logging()

    def _setup_logging(self):
        """设置标准logging配置"""
        # 创建logger
        logger = logging.getLogger("epuber")
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        # 清除现有的handlers
        logger.handlers.clear()

        # 添加RichHandler
        handler = RichHandler(
            console=self.console,
            show_time=False,
            show_path=False,
            enable_link_path=False,
            markup=True,
            rich_tracebacks=True,
        )
        logger.addHandler(handler)
        self.logger = logger

    def info(self, message: str, *args, **kwargs):
        """信息级别日志"""
        self.logger.info(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        """调试级别日志（仅在verbose模式下显示）"""
        self.logger.debug(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """警告级别日志"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """错误级别日志"""
        self.logger.error(message, *args, **kwargs)

    def success(self, message: str):
        """成功消息"""
        text = Text(message, style="bold green")
        self.console.print(text)

    def failure(self, message: str):
        """失败消息"""
        text = Text(message, style="bold red")
        self.console.print(text)

    def step(self, step_num: int, message: str):
        """步骤消息"""
        text = Text(f"[{step_num}] {message}", style="cyan")
        self.console.print(text)

    def progress_start(self, message: str):
        """开始进度"""
        if self.verbose:
            text = Text(f"开始: {message}", style="blue")
            self.console.print(text)

    def progress_complete(self, message: str):
        """完成进度"""
        if self.verbose:
            text = Text(f"完成: {message}", style="green")
            self.console.print(text)


# 全局logger实例
_global_logger: Optional[Logger] = None


def get_logger(verbose: bool = False) -> Logger:
    """获取全局logger实例"""
    global _global_logger
    if _global_logger is None or _global_logger.verbose != verbose:
        _global_logger = Logger(verbose)
    return _global_logger


def setup_logger(verbose: bool = False) -> Logger:
    """设置并返回logger实例"""
    return get_logger(verbose)
