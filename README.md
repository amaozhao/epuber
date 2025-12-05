# epuber

[![PyPI version](https://badge.fury.io/py/epuber.svg)](https://pypi.org/project/epuber/)
[![Python versions](https://img.shields.io/pypi/pyversions/epuber)](https://pypi.org/project/epuber/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

EPUB小说生成器 - 将TXT小说转换为标准EPUB格式电子书

## 功能特性

- 🏗️ **智能解析**：自动识别小说章节结构，支持卷、章、番外等层级
- 🌐 **多编码支持**：自动检测UTF-8、GBK、Big5等多种字符编码
- 🎨 **美观排版**：内置CSS样式，生成符合EPUB标准的美观电子书
- 🖼️ **自动封面**：智能生成精美封面，支持多种样式（默认、优雅、现代、经典）
- ⚡ **命令行工具**：简单易用的CLI界面，支持自定义配置
- 🔧 **正则表达式**：支持自定义章节识别规则
- 📖 **多格式支持**：支持添加封面图片等元数据
- 🌍 **跨平台**：支持Windows、macOS、Linux

## 安装

### 下载可执行文件（推荐）

从 [GitHub Releases](https://github.com/amaozhao/epuber/releases) 下载对应平台的预编译可执行文件：

- **macOS**: `epuber-macos-x86_64` 或 `epuber-macos-arm64`
- **Windows**: `epuber-windows-x86_64.exe`
- **Linux**: `epuber-linux-x86_64`

下载后直接运行，无需安装Python环境。

### 从PyPI安装

```bash
pip install epuber
```

安装完成后可以使用 `epuber` 命令。

### 封面样式

项目支持4种自动生成的封面样式：

- **default**: 蓝色渐变背景，经典布局
- **elegant**: 金色主题，优雅大方
- **modern**: 几何图案，现代风格
- **classic**: 古风设计，传统美学

### 从源码安装

```bash
git clone https://github.com/amaozhao/epuber.git
cd epuber
pip install -e .
```

## 使用方法

### 基本用法

```bash
# 生成EPUB文件（自动保存到输入文件同目录）
epuber generate novel.txt --author "作者名"

# 指定输出目录
epuber generate novel.txt --output ./output --author "作者名"

# 启用详细日志
epuber generate novel.txt --author "作者名" --verbose
```

### 高级用法

```bash
# 自定义章节识别正则表达式
epuber generate novel.txt \
  --author "作者名" \
  --volume-regex "^第[一二三四五六七八九十]+卷" \
  --chapter-regex "^第[0-9]+章" \
  --exclude-regex "^免责声明"

# 添加封面图片
epuber generate novel.txt \
  --author "作者名" \
  --cover cover.jpg

# 使用不同样式的自动封面
epuber generate novel.txt \
  --author "作者名" \
  --cover-style elegant

# 验证EPUB文件格式
epuber validate output.epub
```

### 命令行选项

```
Usage: epuber [OPTIONS] COMMAND [ARGS]...

EPUB 生成器 - 将小说文本转换为 EPUB 格式

Options:
  --help  Show this message and exit.

Commands:
  generate  生成 EPUB 文件
  validate  验证 EPUB 文件格式
```

#### generate 命令

```
Usage: epuber generate [OPTIONS] INPUT

生成 EPUB 文件

Arguments:
  INPUT  输入小说文件路径  [required]

Options:
  -o, --output TEXT          输出目录，默认为输入文件所在目录
  --author TEXT              作者姓名  [default: AmaoZhao]
  --language TEXT            语言代码  [default: zh-CN]
  --cover FILE               封面图片路径
  --cover-style TEXT         自动封面样式  [default: default]
  --volume-regex TEXT        自定义卷标题正则表达式
  --chapter-regex TEXT       自定义章节标题正则表达式
  --exclude-regex TEXT       自定义排除模式正则表达式
  -v, --verbose              启用详细日志输出
  --help                     Show this message and exit.
```

#### validate 命令

```
Usage: epuber validate [OPTIONS] INPUT_FILE

验证 EPUB 文件格式

Arguments:
  INPUT_FILE  要验证的 EPUB 文件  [required]

Options:
  -v, --verbose  启用详细日志输出
  --help         Show this message and exit.
```

## 项目结构

```
epuber/
├── epuber/              # 主包
│   ├── __init__.py
│   ├── parser.py        # 文件解析器
│   ├── processor.py     # 文本处理器
│   ├── writer.py        # EPUB写入器
│   ├── generator.py     # 主协调器
│   ├── logging.py       # 日志系统
│   ├── exceptions.py    # 自定义异常
│   ├── schemas.py       # 数据模型
│   └── templates/       # 模板文件
├── tests/               # 测试文件
├── docs/                # 文档
└── main.py              # CLI入口
```

## 开发

### 环境设置

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
ruff format .

# 代码检查
ruff check . --fix
```

### 构建可执行文件

#### 使用PyInstaller创建单文件可执行程序

```bash
# 安装PyInstaller
pip install pyinstaller

# 构建单文件可执行程序
pyinstaller --onefile --name epuber main.py

# 生成的可执行文件位于 dist/ 目录
```

#### 构建Python分发包

```bash
# 安装构建工具
pip install build

# 构建wheel和sdist包
python -m build

# 上传到PyPI（需要API token）
twine upload dist/*
```

#### 跨平台构建

项目包含GitHub Actions工作流，可自动构建多平台可执行文件：

- **macOS**: x86_64 和 ARM64
- **Windows**: x86_64
- **Linux**: x86_64

推送tag到GitHub时会自动触发构建，生成的可执行文件可在Releases页面下载。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

- [ebooklib](https://github.com/aerkalov/ebooklib) - EPUB文件处理库
- [typer](https://github.com/tiangolo/typer) - 命令行界面框架
- [chardet](https://github.com/chardet/chardet) - 字符编码检测库
- [rich](https://github.com/Textualize/rich) - 终端美化库
- [Pillow](https://github.com/python-pillow/Pillow) - 图像处理库