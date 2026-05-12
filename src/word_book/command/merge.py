from pathlib import Path
from typing import Annotated, cast

import rich
import typer

from ..core.book_discovery import ensure_book_file, discover_book_path
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
    config: AppConfig = cast(AppConfig, ctx.obj)
    if main_book_path is None:
        main_book_path = ensure_book_file(config.main_book_path, label="主词书")
    else:
        main_book_path = discover_book_path(main_book_path, config)
    
    other_book_path = discover_book_path(other_book_path, config)

    try:
        with main_book_path.open("r", encoding="utf-8") as file:
            existing: set[str] = {line.strip() for line in file if line.strip()}
        with other_book_path.open("r", encoding="utf-8") as file:
            other_words: set[str] = {line.strip() for line in file if line.strip()}
    except OSError as exc:
        abort(f"读取词书失败: {exc}")

    new_words: set[str] = other_words - existing

    if new_words:
        _ = append_lines_to_file(new_words, main_book_path)
        rich.print(f"已合并 {len(new_words)} 个新单词.")
        return

    rich.print("没有新单词需要合并.")
