from pathlib import Path
from typing import Annotated
import textwrap

import rich
import typer

from ..core.config import CONFIG_DIR_NAME, ENV_CONFIG_FILE_NAME, TOML_CONFIG_FILE_NAME
from ..core.exceptions import abort

app = typer.Typer()


# 定义模板常量
DEFAULT_ENV = textwrap.dedent("""
    API_KEY=""
    LLM_BASE_URL=""
    LLM_MODEL="deepseek-ai/DeepSeek-V3.2"
""").strip()


def build_default_toml(main_book_path: str) -> str:
    return textwrap.dedent(
        f"""
        title = "My Word Book"
        [settings]
        main_book_path = "{main_book_path}"
        """
    ).strip()


def get_init_paths(global_config: bool) -> tuple[Path, Path, Path, str]:
    base_dir = Path.home() if global_config else Path.cwd()
    config_dir = base_dir / CONFIG_DIR_NAME
    toml_file = config_dir / TOML_CONFIG_FILE_NAME
    env_file = config_dir / ENV_CONFIG_FILE_NAME
    default_main_book_path = str((base_dir / "word_book.md").resolve()) if global_config else "word_book.md"
    return config_dir, toml_file, env_file, default_main_book_path


def _ensure_init_target_is_usable(
    config_dir: Path,
    toml_file: Path,
    env_file: Path,
    *,
    scope_label: str,
    force: bool,
) -> None:
    existing_files = [file_path.name for file_path in (toml_file, env_file) if file_path.exists()]

    if not config_dir.exists():
        return

    if not config_dir.is_dir():
        abort(f"{scope_label} 配置路径 `{config_dir}` 已存在且不是目录。")

    if existing_files and not force:
        existing_text = "、".join(f"`{file_name}`" for file_name in existing_files)
        abort(f"{scope_label} 配置目录 `{config_dir}` 已存在 {existing_text}，请先删除后再初始化。")


@app.command()
def init(
    project_config: Annotated[
        bool,
        typer.Option("--project", help="在当前项目目录创建项目配置。"),
    ] = False,
    global_config: Annotated[
        bool,
        typer.Option("--global", help="在用户主目录创建全局配置。"),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="覆盖已有的 .bookconfig 配置文件。"),
    ] = False,
) -> str | None:
    """初始化项目或全局配置。"""
    if project_config and global_config:
        abort("`--project` 和 `--global` 不能同时使用。")

    if global_config:
        config_dir, toml_file, env_file, default_main_book_path = get_init_paths(True)
        scope_label = "全局"
    else:
        config_dir, toml_file, env_file, default_main_book_path = get_init_paths(False)
        scope_label = "项目"

    _ensure_init_target_is_usable(
        config_dir,
        toml_file,
        env_file,
        scope_label=scope_label,
        force=force,
    )

    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        rich.print(f"已创建{scope_label}配置目录: {config_dir}")

        if force:
            rich.print(f"提示: {scope_label}配置目录已存在，将覆盖写入配置文件。")

        toml_file.write_text(build_default_toml(default_main_book_path), encoding="utf-8")  # pyright: ignore[reportUnusedCallResult]
        rich.print(f"已生成文件: {toml_file.name}")

        env_file.write_text(DEFAULT_ENV, encoding="utf-8")  # pyright: ignore[reportUnusedCallResult]
        rich.print(f"已生成文件: {env_file.name}")
        rich.print("✨ 初始化成功!")
    except OSError as exc:
        abort(f"初始化失败: {exc}")

    return None
