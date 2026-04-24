from pathlib import Path
from typing import Annotated, cast

import rich
import typer

from ..core.config import AppConfig
from ..core.exceptions import abort
from ..core.output_writer import append_lines_to_file

app = typer.Typer()


@app.command()
def add(
    ctx: typer.Context,
    word: Annotated[str, typer.Argument(help="要添加的单词")],
    book_path: Annotated[
        Path | None,
        typer.Option(
            None,
            "--file",
            "-f",
            help="词书路径",
            file_okay=True,
            dir_okay=False,
        ),
    ] = None,
) -> None:
    """添加单词到词书"""
    if book_path is None:
        config: AppConfig = cast(AppConfig, ctx.obj)
        book_path = config.main_book_path

    if not book_path.exists():
        abort(f"词书 `{book_path}` 不存在。")
    if not book_path.is_file():
        abort(f"词书路径 `{book_path}` 不是文件。")

    try:
        with book_path.open("r", encoding="utf-8") as file:
            existing: set[str] = {line.strip() for line in file if line.strip()}
    except OSError as exc:
        abort(f"读取词书 `{book_path}` 失败: {exc}")

    if word in existing:
        rich.print(f"[yellow]{word}[/yellow] 已经在词书里了.")
        return

    append_lines_to_file([word], book_path)

    rich.print(f"[green]{word}[/green] 已经添加到词书里了.")
