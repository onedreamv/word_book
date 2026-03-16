from cli import AppConfig
import typer
from pathlib import Path
import rich
from typing import Annotated


app = typer.Typer()

@app.command()
def add(
        ctx: typer.Context,
        word: Annotated[str, typer.Argument(help="要添加的单词")], 
        book_path: Annotated[Path, typer.Option("--file","-f", help="词书路径")]
        ):
    """添加单词到词书"""
    if not book_path:
        config: AppConfig = ctx.obj
        book_path = config.toml_config["word_book"]["path"]

    with open(book_path, "r", encoding="utf-8") as f:
        existing: set[str] = {line.strip() for line in f if line.strip()}
    
    if word in existing:
        rich.print(f"{word} 已经在词书里了.")
    else:
        with open(book_path, "a", encoding="utf-8") as f:
            rich.print(f.write(word + "\n"))
        rich.print(f"{word} 已经添加到词书里了.")
