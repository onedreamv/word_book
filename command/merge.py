from ..core.config import AppConfig
from typing import Annotated, cast
import typer
from pathlib import Path
import rich

app = typer.Typer()

@app.command()
def merge(
    ctx: typer.Context,
    other_book_path: Annotated[Path, typer.Argument(help="要合并的词书路径")], 
    main_book_path: Annotated[Path | None, typer.Option("--file","-f", help="主词书路径")] = None
    ):
    """合并其他词书到主词书"""
    if not main_book_path:
        config = cast(AppConfig, ctx.obj)
        main_book_path = Path(config.toml_config["settings"]["main_book_path"])
    
    with open(main_book_path, "r", encoding="utf-8") as f:
        existing: set[str] = {line.strip() for line in f if line.strip()}
    
    with open(other_book_path, "r", encoding="utf-8") as f:
        other_words: set[str] = {line.strip() for line in f if line.strip()}
    
    new_words = other_words - existing
    
    if new_words:
        with open(main_book_path, "a", encoding="utf-8") as f:
            for word in new_words:
                f.write('\n' + word)
        rich.print(f"已合并 {len(new_words)} 个新单词.")
    else:
        rich.print("没有新单词需要合并.")
