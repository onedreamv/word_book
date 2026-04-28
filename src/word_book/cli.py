import rich
import typer
from typing import Annotated

from .command import app as command_app
from .core.config import AppConfig, ConfigError, load_app_config
from .core.exceptions import abort

app: typer.Typer = typer.Typer()

# 注册命令
app.add_typer(command_app, name=None)


def version_callback(value: bool) -> None:
    """显示版本信息并退出。"""
    if value:
        from .core.version import APPNAME, VERSION

        rich.print(f"{APPNAME} {VERSION}")
        raise typer.Exit()


@app.callback()
def main_callback(ctx: typer.Context,
                version: Annotated[bool, typer.Option
                ("--version", "-v", 
                help="显示版本信息并退出。", 
                callback=version_callback, 
                is_eager=True)] = False
                  ) -> None:
    """管理个人词书的 CLI 工具。"""
    # CLI 主回调：加载配置并确保默认词书存在。
    if ctx.resilient_parsing:
        return

    if ctx.invoked_subcommand == "init":
        return

    try:
        config: AppConfig = load_app_config()
    except ConfigError as exc:
        abort(str(exc), ctx=ctx)

    ctx.obj = config

    if config.main_book_path.exists():
        return

    try:
        config.main_book_path.touch()
    except OSError as exc:
        abort(f"创建默认词书 `{config.main_book_path}` 失败: {exc}", ctx=ctx)

    rich.print(f"提示: 默认词书 {config.main_book_path} 不存在，已自动创建。")
