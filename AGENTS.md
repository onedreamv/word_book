# CODEBUDDY.md This file provides guidance to CodeBuddy when working with code in this repository.

## 常用命令

- **安装依赖**：`uv sync`。根据 `pyproject.toml` 与 `uv.lock` 同步运行环境，是本仓库默认依赖管理方式。
- **运行 CLI（文档口径）**：`uv run python cli.py <command>`。可用子命令见 `command/__init__.py`：`init`、`add`、`clean`、`merge`。
- **运行 `init`**：`uv run python cli.py init`，或 `uv run python cli.py init --global`。前者初始化项目级 `.bookconfig`，后者初始化用户目录全局配置。
- **运行 `add`**：`uv run python cli.py add <word> [--file|-f <book_path>]`。未提供 `--file` 时使用配置中的主词书。
- **运行 `clean`**：`uv run python cli.py clean [source] [--clip] [--edit]`。输入可来自文件、`stdin`、剪贴板或编辑器，输出到配置 `working_dir` 下的唯一文件名（如 `cleaned.txt`）。
- **运行 `merge`**：`uv run python cli.py merge <other_book_path> [--file|-f <main_book_path>]`。将外部词书去重合并到主词书。
- **类型检查**：`uv run pyright`（或 `uvx pyright`）。仓库存在 `pyright` 忽略注释，建议改动后执行。
- **代码检查（lint）**：`uvx ruff check .`。仓库未提供额外 Ruff 配置，按默认规则检查。
- **测试（全量）**：当前仓库未包含测试文件；新增测试后使用 `uv run pytest`。
- **测试（单个用例）**：当前仓库未包含测试文件；新增测试后使用 `uv run pytest path/to/test_file.py::test_function_name`。

## 高层架构（Big Picture）

本项目是一个基于 Typer 的命令行词书工具，架构上分为**CLI 交互层**（`cli.py` + `command/`）与**核心能力层**（`core/`）。设计目标是：命令编排与业务能力解耦，使配置解析、输入源处理、LLM 调用与文件写入可复用。

### 1) 入口与生命周期

- 全局入口在 `cli.py`，Typer 根应用挂载 `command/` 下的所有子命令。
- `main_callback` 是统一前置流程：
  - 如果调用的是 `init`，跳过配置加载（因为初始化前可能没有配置）。
  - 其他命令先 `load_app_config()`，将 `AppConfig` 注入 `ctx.obj`。
  - 确保默认主词书文件存在，不存在则自动创建。
- 因此，除 `init` 外，命令实现都依赖 `ctx.obj` 提供运行时配置，不重复各自做配置发现与校验。

### 2) 配置系统是全局枢纽

配置逻辑集中在 `core/config.py`，其行为决定大多数命令的运行语义：

- 配置发现顺序：从当前目录向上查找项目级 `.bookconfig`；找不到再回退到用户主目录 `.bookconfig`。
- 配置目录完整性：必须同时存在 `config.toml` 与 `config.env`，缺失即报错。
- 路径规则：
  - project 配置允许相对 `main_book_path`，相对于项目工作目录解析。
  - global 配置要求 `main_book_path` 是绝对路径。
- `load_app_config()` 最终产出 `AppConfig`：包含 `config_dir`、`working_dir`、`main_book_path`、`env_config`、`config_source`。

这使得 `add`、`merge`、`clean` 等命令都能在统一语义下工作（尤其是默认词书位置与输出目录）。

### 3) 命令层职责划分

`command/__init__.py` 注册四个子命令，分别关注一个用户动作：

- `book_init.py`（`init`）：创建 `.bookconfig` 与默认模板文件。
- `add.py`（`add`）：向词书追加一个词，先读现有词集做去重。
- `merge.py`（`merge`）：读主词书与待合并词书，按集合差集追加新词。
- `clean.py`（`clean`）：从多输入源取文本，调用 LLM 提取词，再写入新输出文件。

命令层以“编排”为主：参数解析、选择输入输出、调用 core 能力、输出提示，不承载底层通用细节。

### 4) `clean` 命令的数据流（核心业务链路）

`clean` 是最复杂路径，数据流如下：

1. `core/text_source.py::resolve_input_text` 统一处理输入来源（文件 / `-` / 管道 / `--clip` / `--edit`），并做空文本与长度校验。
2. 从 `AppConfig.env_config` 读取 `API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`。
3. `core/llm_client.py::OpenAIClient.chat` 发起模型调用；`WordExtractor` 在命令层负责提示词构建与 JSON 结果解析。
4. `core/output_writer.py` 负责冲突文件名生成（`resolve_unique_path`）和写入。

这个链路体现了“命令层做业务编排，core 层做能力封装”的总体设计。

### 5) 错误处理与可维护性约束

- 统一错误出口是 `core/exceptions.py::abort()`：打印统一错误样式并 `typer.Exit`。
- 多个核心模块（配置、文本输入、LLM、写文件）都直接使用 `abort()`，避免散落的 `print + exit`。
- 未来扩展命令时，建议遵循已有边界：
  - 参数与交互在 `command/`；
  - 可复用逻辑沉淀到 `core/`；
  - 配置与路径语义始终通过 `AppConfig` 驱动。

## 现状说明（避免误判）

- 仓库当前**没有**测试文件与测试配置。
- 仓库当前**没有**统一格式化命令配置（如 `ruff format`/`black` 配置块）。
- `pyproject.toml` 当前未声明 console script；CLI 运行方式以仓库文档与本文件命令区为准。