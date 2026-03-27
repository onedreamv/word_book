import typer

from .book_init import app as init_app
from .add import app as add_app
from .clean import app as clean_app
from .merge import app as merge_app

app = typer.Typer()

app.add_typer(init_app, name="init")
app.add_typer(add_app, name="add")
app.add_typer(clean_app, name="clean")
app.add_typer(merge_app, name="merge")
