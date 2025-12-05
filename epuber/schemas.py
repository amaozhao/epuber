"""
Epuber 数据模型定义
使用 Pydantic 定义 Volume 和 Chapter 数据结构
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class Chapter(BaseModel):
    """章节数据模型"""

    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    content_type: str = Field("chapter", description="内容类型: chapter(章节), extra(番外), notice(公告), postscript(后记)")
    order: Optional[int] = Field(None, description="章节顺序")


class Volume(BaseModel):
    """卷数据模型"""

    title: Optional[str] = Field(None, description="卷标题")
    chapters: List[Chapter] = Field(default_factory=list, description="卷中的章节列表")
    order: Optional[int] = Field(None, description="卷顺序")


class EpubMetadata(BaseModel):
    """EPUB 元数据模型"""

    title: str = Field(..., description="书籍标题")
    author: str = Field(..., description="作者姓名")
    language: str = Field("zh-CN", description="语言代码")
    identifier: Optional[str] = Field(None, description="书籍标识符")
    description: Optional[str] = Field(None, description="书籍描述")
    publisher: Optional[str] = Field(None, description="出版商")
    date: Optional[str] = Field(None, description="出版日期")
    rights: Optional[str] = Field(None, description="版权信息")


class EpubConfig(BaseModel):
    """EPUB 生成配置模型"""

    metadata: EpubMetadata = Field(..., description="EPUB 元数据")
    volumes: List[Volume] = Field(default_factory=list, description="卷列表")
    cover_image: Optional[str] = Field(None, description="封面图片路径")
    css_template: Optional[str] = Field(None, description="CSS 模板路径")
    output_format: str = Field("epub", description="输出格式")
