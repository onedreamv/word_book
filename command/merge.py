from pathlib import Path
from typing import Annotated, cast

import rich
import typer

from ..core.config import AppConfig
from ..core.exceptions import abort
from ..core.output_writer import append_lines_to_file

app = typer.Typer()


@app.command()
def merge(
    ctx: typer.Context,
    other_book_path: Annotated[Path, typer.Argument(help="要合并的词书路径")],
    main_book_path: Annotated[Path | None, typer.Option("--file", "-f", help="主词书路径")] = None,
) -> None:
    """合并其他词书到主词书"""
    if main_book_path is None:
        config: AppConfig = cast(AppConfig, ctx.obj)
        main_book_path = config.main_book_path

    if not main_book_path.exists():
        abort(f"主词书 `{main_book_path}` 不存在。")
    if not main_book_path.is_file():
        abort(f"主词书路径 `{main_book_path}` 不是文件。")
    if not other_book_path.exists():
        abort(f"待合并词书 `{other_book_path}` 不存在。")
    if not other_book_path.is_file():
        abort(f"待合并词书路径 `{other_book_path}` 不是文件。")

    try:
        with main_book_path.open("r", encoding="utf-8") as file:
            existing: set[str] = {line.strip() for line in file if line.strip()}
        with other_book_path.open("r", encoding="utf-8") as file:
            other_words: set[str] = {line.strip() for line in file if line.strip()}
    except OSError as exc:
        abort(f"读取词书失败: {exc}")

    new_words: set[str] = other_words - existing

    if new_words:
        append_lines_to_file(new_words, main_book_path)
        rich.print(f"已合并 {len(new_words)} 个新单词.")
        return

    rich.print("没有新单词需要合并.")
