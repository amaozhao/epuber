# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-XX

### Added
- ✨ 初始版本发布
- 🏗️ 智能小说章节解析，支持卷、章、番外等多层级结构
- 🌐 自动字符编码检测，支持UTF-8、GBK、Big5等多种编码
- 🎨 内置CSS样式，美观的EPUB排版
- ⚡ 命令行界面，支持丰富的配置选项
- 🔧 可自定义正则表达式规则
- 📖 支持封面图片等元数据
- 🛡️ 完善的异常处理体系
- 📊 详细的日志输出（支持verbose模式）
- 🧪 完整的单元测试套件

### Features
- 解析TXT小说文件并转换为标准EPUB格式
- 自动识别章节标题和层级结构
- 支持多种中文字符编码
- 生成兼容EPUB 2.0和3.0标准的电子书
- 命令行工具，支持批量处理

### Technical
- 使用Python 3.10+兼容性
- 依赖管理：chardet, ebooklib, pydantic, rich, typer
- 构建工具：hatchling
- 代码质量：ruff格式化和检查
- CI/CD：GitHub Actions多平台构建
