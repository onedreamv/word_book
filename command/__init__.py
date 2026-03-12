import typer

from .book_init import app as init_app




app = typer.Typer()

app.add_typer(init_app, name="init")
