# AGENTS.md

本文件为代码智能体提供最小化的项目指引，详细文档见 [README.md](README.md)。

## 常用命令

- **安装依赖**：`uv sync`。
- **运行 CLI（推荐）**：`uv run wordbook <command>`（脚本入口见 `pyproject.toml`）。
- **可用子命令**：`init`、`add`、`clean`、`merge`（挂载于 `src/word_book/command/`）。
- **类型检查**：`uv run pyright`（或 `uvx pyright`）。
- **代码检查（lint）**：`uvx ruff check .`。
- **测试**：当前仓库未包含测试文件；新增测试后使用 `uv run pytest`。

## 架构要点（最常用的跳转）

- CLI 入口与生命周期：`src/word_book/cli.py` 中 `main_callback` 统一加载配置并创建默认词书。
- 命令编排层：`src/word_book/command/`，每个文件对应一个子命令。
- 核心能力层：`src/word_book/core/`，包含配置解析、文本输入、LLM 调用与输出写入。
- 错误出口统一：`src/word_book/core/exceptions.py::abort()`。

## 需要注意的行为约束

- `init` 命令会跳过配置加载；其余命令必须依赖 `AppConfig`（由 `load_app_config()` 注入 `ctx.obj`）。
- `.bookconfig` 既可项目级也可全局，路径解析规则在 `core/config.py` 中定义。