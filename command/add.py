from ..core.config import AppConfig
from typing import Annotated, cast
import typer
from pathlib import Path
import rich


app = typer.Typer()

@app.command()
def add(
        ctx: typer.Context,
        word: Annotated[str, typer.Argument(help="要添加的单词")], 
        book_path: Annotated[Path | None, typer.Option("--file", "-f", help="词书路径",
        file_okay=True,dir_okay=False,
        )] = None
        ):
    """添加单词到词书"""
    if not book_path:
        config = cast(AppConfig, ctx.obj)
        book_path = Path(config.toml_config["settings"]["main_book_path"])

    if not book_path.exists():
        rich.print(f"错误: 词书 {book_path} 不存在。")
        raise typer.Exit(code=1)

    with open(book_path, "r", encoding="utf-8") as f:
        existing: set[str] = {line.strip() for line in f if line.strip()}
    
    if word in existing:
        rich.print(f"[yellow]{word}[/yellow] 已经在词书里了.")
    else:
        with open(book_path, "a", encoding="utf-8") as f:
            f.write(word + "\n")
        rich.print(f"[green]{word}[/green] 已经添加到词书里了.")
