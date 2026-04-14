from pathlib import Path
from typing import cast
import typer
import rich
from dotenv import dotenv_values
import tomllib
from .core.config import get_config_dir, NotFoundConfigDirError, AppConfig, Settings
from .command import app as command_app

app : typer.Typer = typer.Typer()

# 注册命令
app.add_typer(command_app, name=None)

# typer主回调
@app.callback()
def main_callback(ctx: typer.Context):
    # """主回调函数，用于初始化配置"""

    # 如果是初始化子命令，直接返回
    if ctx.invoked_subcommand == "init":
        return
    # 如果不是init 尝试初始化配置目录
    try:
        config_dir, toml_path, env_path = get_config_dir()
    except NotFoundConfigDirError:
        rich.print(f"Error: 配置文件不存在")
        raise typer.Exit(code=1)
    
    #配置文件存在,读取配置
    try:
        with open(toml_path, "rb") as f:
            toml_config= tomllib.load(f)
            env_config = dotenv_values(env_path)
        # 存储配置到上下文
        settings_obj: Settings =  Settings(**toml_config["settings"])  # pyright: ignore[reportAny]

        ctx.obj = AppConfig(
        config_dir=config_dir,
        toml_config=settings_obj,
        env_config=env_config
        )
    except Exception as e:
        rich.print(f"读取配置文件失败: {e}")
        raise typer.Exit(code=1)

    # 检查默认词书是否存在,如果不存在则创建
    config: AppConfig = cast(AppConfig, ctx.obj)
    default_book_path: Path = Path(config.toml_config.main_book_path)
    if not default_book_path.exists():
        default_book_path.touch()
        rich.print(f"提示: 默认词书 {default_book_path} 不存在，已自动创建。")
    

if __name__ == "__main__":
    app()



    

