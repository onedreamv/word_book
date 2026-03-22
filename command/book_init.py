import rich
import typer
from pathlib import Path
import textwrap

app = typer.Typer()

# 定义模版常量
DEFAULT_TOML = textwrap.dedent("""
    title = "My Word Book"
    [settings]
    main_book_path = "word_book.md"
""").strip()

DEFAULT_ENV = textwrap.dedent("""
    API_KEY=""
    LLM_BASE_URL=""
    LLM_MODEL="deepseek-ai/DeepSeek-V3.2"
""").strip()


@app.command()
def init() -> str | None:
    """初始化项目：创建 .bookconfig 目录及默认配置文件。"""
    cwd = Path.cwd()
    config_dir = cwd / ".bookconfig"
    toml_file = config_dir / "config.toml"
    env_file = config_dir / "config.env"

    # 检查是否已存在配置目录
    if config_dir.exists():
        return f"提示: {config_dir} 已经存在，无需初始化。"
    
    try:
        # 创建目录
        config_dir.mkdir(parents=True, exist_ok=True)
        rich.print(f"已创建目录: {config_dir}")
        # 写入文件
        toml_file.write_text(DEFAULT_TOML, encoding="utf-8")  # pyright: ignore[reportUnusedCallResult]
        rich.print(f"已生成文件: {toml_file.name}")
        env_file.write_text(DEFAULT_ENV, encoding="utf-8")  # pyright: ignore[reportUnusedCallResult]
        rich.print(f"已生成文件: {env_file.name}")
        # 反馈成功
        rich.print("✨ 初始化成功!")
        
    except Exception as e:
        rich.print(f"❌ 初始化失败: {e}")
        raise typer.Exit(code=1)