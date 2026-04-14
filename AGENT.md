# CODEBUDDY.md 本文件旨在为 CodeBuddy 处理此代码库的代码时提供指导。

## 常用命令

- **运行 CLI**：使用 `uv run python cli.py [command]` 运行应用命令（例如：`init`、`add`、`clean`、`merge`）。
- **安装依赖**：使用 `uv sync` 安装 `pyproject.toml` 和 `uv.lock` 中定义的项目依赖。
- **类型检查 / 规范检查**：代码库使用 `pyright` 进行静态类型检查（代码中可见 `# pyright: ignore` 注释）。使用 `uv run pyright` 或 `uvx pyright` 运行类型检查。对于代码检查，推荐使用标准工具如 `uvx ruff check .`。
- **运行测试**：目前没有专门的测试文件。但在未来添加测试后，请使用标准的 `uv run pytest`。要运行单个测试，请使用 `uv run pytest path/to/test_file.py::test_function_name`。

## 架构与结构

本项目是一个使用 Typer 构建的 CLI 工具，用于管理生词本（"word book"），并使用大语言模型（LLM）从各种文本源中提取单词。

### 1. 应用入口 (`cli.py`)
根目录下的 `cli.py` 是主入口点。它实例化了 Typer 应用，注册了来自 `command/` 包的子命令，并通过 Typer 回调函数 (`main_callback`) 处理全局初始化。该回调负责解析 `.bookconfig` 目录，加载配置（`config.toml` 和 `config.env`），将实例化的 `AppConfig` 注入到 Typer 上下文（`ctx.obj`）中，并确保主生词本文件已存在。

### 2. 命令模块 (`command/`)
此目录定义了 CLI 子命令。每个命令都是一个独立的 Typer 命令/应用，在 `command/__init__.py` 中被统一汇总。
- **`add.py`**：将单个单词追加到配置的主生词本中，并进行查重处理。
- **`clean.py`**：一个较为复杂的命令，负责从配置的输入源读取文本并进行清理，然后将其委托给 `WordExtractor`，利用 LLM 提取标准的英文单词，最后将结果输出到新文件。
- **`merge.py`**：将多个生词本合并为一个集合。
- **`book_init.py`**：初始化 `.bookconfig` 目录以及必需的配置文件。

各命令通常通过将 `ctx.obj` 显式转换为 `AppConfig` 类型来读取配置。

### 3. 核心逻辑与工具类 (`core/`)
`core/` 包包含了与 CLI 路由解耦的业务逻辑、领域抽象和辅助函数。
- **`config.py`**：包含定义配置结构的数据类（`Settings`、`AppConfig`）和用于定位项目配置目录的工具函数（`get_config_dir`）。
- **`llm_client.py`**：定义了与大语言模型交互的协议（`LLMClient`）及其具体实现（`OpenAIClient`）。它强制执行词汇提取时返回标准 JSON 格式，将底层的 OpenAI API 调用细节封装了起来。
- **`text_source.py`**：提供了非常灵活的文本输入读取工具，支持从文件、标准输入 (stdin)、系统剪贴板（基于 `pyperclip`）或交互式编辑器（`typer.edit`）读取文本，同时处理了文本字数限制和各种错误。
- **`output_writer.py`**：包含将单词列表安全写入文件并智能解决输出路径冲突（例如自动递增生成唯一的文件名）的辅助函数。
- **`exceptions.py`**：提供集中式的异常处理和退出逻辑封装（例如打印统一样式的错误消息并抛出 `typer.Exit`）。

通过将 CLI 交互层保留在 `command/` 目录下，并将纯业务逻辑和外部集成保留在 `core/` 目录下，该项目保持了高度的模块化，并且非常易于测试。
