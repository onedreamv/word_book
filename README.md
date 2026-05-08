# word-book

一个基于 Typer 的 CLI 工具，用于维护个人词书。支持从文本中自动提取生词、管理单词列表、合并多个词书。

## 功能特性

- **单词管理**: 快速添加、删除单词到个人词书
- **智能提取**: 使用 LLM 从长文本中自动提取生词
- **多来源输入**: 支持从文件、剪贴板、编辑器输入文本
- **词书合并**: 合并多个词书并自动去重
- **双配置模式**: 支持项目级和全局级配置

## 快速开始

### 构建与安装

推荐使用 UV build 构建 wheel 包：

```bash
uv build
```

安装 wheel 包：

```bash
pip install --user dist/wordbook.whl
```

安装 Typer 补全：

```bash
wordbook --install-completion
```

### 初始化配置

```bash
wordbook init
wordbook init --global
wordbook init --force
```

## 命令示例

### init - 初始化配置

```bash
wordbook init
wordbook init --global
wordbook init --force
```

### add - 添加单词

```bash
wordbook add apple
wordbook add apple --file my_words.txt
```

### clean - 智能提取生词

```bash
wordbook clean article.txt
wordbook clean --clip
wordbook clean --edit
echo "Hello world" | wordbook clean -
```

### merge - 合并词书

```bash
wordbook merge other_book.txt
wordbook merge other_book.txt --file main_book.txt
```

## 配置说明

### 配置文件位置

- **项目配置**: 当前目录下的 `.bookconfig/`
- **全局配置**: 用户主目录下的 `.bookconfig/`

### 配置文件结构

```
.bookconfig/
├── config.toml    # 主配置文件
└── config.env     # 环境变量配置
```

### config.toml 示例

```toml
title = "My Word Book"
[settings]
main_book_path = "word_book.md"
```

### config.env 示例

```env
API_KEY=your-api-key-here
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-ai/DeepSeek-V3.2
```

## 技术栈

- **Python 3.13+**
- **Typer** - CLI 框架
- **Rich** - 终端美化输出
- **OpenAI SDK** - LLM API 调用
- **python-dotenv** - 环境变量管理
- **pyperclip** - 剪贴板操作

## 开发

### 运行测试

```bash
uv run pytest
```

### 类型检查

```bash
uv run pyright
```

### 代码检查

```bash
uvx ruff check .
```

## 项目结构

```
src/
└── word_book/
    ├── cli.py           # CLI 入口
    ├── command/         # 命令模块
    │   ├── add.py       # 添加单词命令
    │   ├── book_init.py # 初始化命令
    │   ├── clean.py     # 清理提取命令
    │   └── merge.py     # 合并命令
    └── core/            # 核心模块
        ├── config.py    # 配置解析
        ├── exceptions.py # 异常处理
        ├── llm_client.py # LLM 客户端
        ├── output_writer.py # 输出写入
        ├── text_source.py # 文本输入
        └── version.py   # 版本信息
```

## 许可证

MIT