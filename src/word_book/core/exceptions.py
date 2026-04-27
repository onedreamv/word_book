import typer
import rich
from typing import Never

def abort(
    message: str,
    *,
    code: int = 1,
    ctx: typer.Context | None = None,
    show_help: bool = False,
) -> Never:
    if show_help and ctx is not None:
        typer.echo(ctx.get_help())
    rich.print(f"[red]错误:[/red] {message}")
    raise typer.Exit(code=code)
