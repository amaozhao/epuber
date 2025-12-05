"""
简洁版封面生成器
"""

import io
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from .exceptions import EpubGenerationError


class Cover:
    """封面生成器"""

    def __init__(self):
        if not HAS_PIL:
            raise EpubGenerationError("需要Pillow库: pip install Pillow")

        self.w, self.h = 800, 1200  # 尺寸
        self.font_big = self._font(72)  # 大字体
        self.font_small = self._font(36)  # 小字体

    def _font(self, size):
        """加载字体"""
        paths = [
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/System/Library/Fonts/STHeiti Light.ttc",  # macOS 备用
            "C:/Windows/Fonts/msyh.ttc",  # Windows 微软雅黑
            "C:/Windows/Fonts/simsun.ttc",  # Windows 宋体
            "C:/Windows/Fonts/msyhbd.ttc",  # Windows 微软雅黑粗体
            "C:/Windows/Fonts/simhei.ttf",  # Windows 黑体
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "/usr/share/fonts/truetype/droid/DroidSansFallback.ttf",  # Linux 备用
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux 中文
        ]

        for p in paths:
            if Path(p).exists():
                return ImageFont.truetype(p, size)

        return ImageFont.load_default()

    def make(self, title: str, author: str, style: str = "default") -> bytes:
        """生成封面

        Args:
            title: 标题
            author: 作者
            style: 样式 (default/elegant/modern/classic)

        Returns:
            PNG数据
        """
        if style == "elegant":
            return self._elegant(title, author)
        elif style == "modern":
            return self._modern(title, author)
        elif style == "classic":
            return self._classic(title, author)
        else:
            return self._default(title, author)

    def _default(self, title: str, author: str) -> bytes:
        """默认样式"""
        img = self._gradient("#2c3e50", "#3498db")
        draw = ImageDraw.Draw(img)

        # 标题位置
        tw = self.font_big.getbbox(title)[2]
        tx = (self.w - tw) // 2
        ty = self.h // 3

        # 作者位置
        aw = self.font_small.getbbox(f"作者：{author}")[2]
        ax = self.w - aw - 50
        ay = self.h - 100

        # 绘制
        self._text_shadow(draw, title, (tx, ty), self.font_big)
        self._text_shadow(draw, f"作者：{author}", (ax, ay), self.font_small)

        return self._png(img)

    def _elegant(self, title: str, author: str) -> bytes:
        """优雅样式"""
        img = self._gradient("#1a1a1a", "#4a4a4a")
        draw = ImageDraw.Draw(img)

        tw = self.font_big.getbbox(title)[2]
        tx = (self.w - tw) // 2
        ty = self.h // 3

        aw = self.font_small.getbbox(f"作者：{author}")[2]
        ax = self.w - aw - 50
        ay = self.h - 100

        self._text_shadow(draw, title, (tx, ty), self.font_big, "#FFD700")
        self._text_shadow(draw, f"作者：{author}", (ax, ay), self.font_small, "#FFD700")

        return self._png(img)

    def _modern(self, title: str, author: str) -> bytes:
        """现代样式"""
        img = Image.new("RGB", (self.w, self.h), "#ffffff")
        draw = ImageDraw.Draw(img)

        # 几何图案
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"]
        for i in range(3):
            x, y = self.w // 2 + (i - 1) * 120, self.h // 2 + (i % 2) * 80
            r = 60 - i * 10
            draw.ellipse([x - r, y - r, x + r, y + r], fill=colors[i], outline=colors[i])

        tw = self.font_big.getbbox(title)[2]
        tx = (self.w - tw) // 2
        ty = self.h // 3

        aw = self.font_small.getbbox(f"作者：{author}")[2]
        ax = self.w - aw - 50
        ay = self.h - 100

        self._text_shadow(draw, title, (tx, ty), self.font_big, "#2c3e50")
        self._text_shadow(draw, f"作者：{author}", (ax, ay), self.font_small, "#34495e")

        return self._png(img)

    def _classic(self, title: str, author: str) -> bytes:
        """经典样式"""
        img = Image.new("RGB", (self.w, self.h), "#f4e4bc")
        draw = ImageDraw.Draw(img)

        # 边框
        draw.rectangle([0, 0, self.w - 1, self.h - 1], outline="#8b4513", width=8)
        draw.rectangle([40, 40, self.w - 40, self.h - 40], outline="#8b4513", width=2)

        tw = self.font_big.getbbox(title)[2]
        tx = (self.w - tw) // 2
        ty = self.h // 3

        aw = self.font_small.getbbox(f"著者：{author}")[2]
        ax = self.w - aw - 50
        ay = self.h - 100

        self._text_shadow(draw, title, (tx, ty), self.font_big, "#8b4513")
        self._text_shadow(draw, f"著者：{author}", (ax, ay), self.font_small, "#654321")

        return self._png(img)

    def _gradient(self, c1: str, c2: str) -> Image.Image:
        """渐变背景"""
        img = Image.new("RGB", (self.w, self.h))
        r1, g1, b1 = self._hex_rgb(c1)
        r2, g2, b2 = self._hex_rgb(c2)

        for y in range(self.h):
            f = y / self.h
            r = int(r1 + (r2 - r1) * f)
            g = int(g1 + (g2 - g1) * f)
            b = int(b1 + (b2 - b1) * f)

            for x in range(self.w):
                img.putpixel((x, y), (r, g, b))

        return img

    def _text_shadow(
        self, draw: ImageDraw.ImageDraw, text: str, pos: tuple, font, color: str = "white", shadow: str = "#34495e"
    ):
        """文字阴影"""
        x, y = pos
        draw.text((x + 2, y + 2), text, font=font, fill=shadow)
        draw.text((x, y), text, font=font, fill=color)

    def _hex_rgb(self, hex_str: str) -> tuple:
        """十六进制转RGB"""
        h = hex_str.lstrip("#")
        return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

    def _png(self, img: Image.Image) -> bytes:
        """转PNG字节"""
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    @classmethod
    def available(cls) -> bool:
        """检查是否可用"""
        return HAS_PIL


# 便捷函数
def make_cover(title: str, author: str, style: str = "default") -> bytes:
    """生成封面"""
    c = Cover()
    return c.make(title, author, style)
