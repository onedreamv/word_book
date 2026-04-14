import sys
from pathlib import Path
import pyperclip
import typer
from .exceptions import abort

MAX_INPUT_CHARS = 200_000

def ensure_text(text: str, *, source_name: str) -> str:
    if not text.strip():
        abort(f"{source_name} 中没有可用文本。")
    if len(text) > MAX_INPUT_CHARS:
        abort(f"{source_name} 过长，超过 {MAX_INPUT_CHARS} 个字符，请分段处理。")
    return text


def load_text_from_file(source: str) -> str:
    file_path = Path(source)

    if not file_path.exists():
        abort(f"输入文件不存在: {file_path}")
    if not file_path.is_file():
        abort(f"输入路径不是文件: {file_path}")

    try:
        return ensure_text(file_path.read_text(encoding="utf-8"), source_name=f"文件 {file_path}")
    except UnicodeDecodeError as exc:
        abort(f"文件不是有效的 UTF-8 文本: {file_path} ({exc})")
    except OSError as exc:
        abort(f"读取文件失败: {file_path} ({exc})")


def load_text_from_stdin() -> str:
    try:
        return ensure_text(sys.stdin.read(), source_name="stdin")
    except OSError as exc:
        abort(f"读取 stdin 失败: {exc}")


def load_text_from_clipboard() -> str:
    try:
        clipboard_text = pyperclip.paste()
    except pyperclip.PyperclipException as exc:
        abort(f"读取剪贴板失败: {exc}")

    return ensure_text(clipboard_text, source_name="剪贴板")


def load_text_from_editor() -> str:
    edited_text = typer.edit(text="", extension=".txt")
    if edited_text is None:
        abort("编辑器输入已取消，未保存任何内容。")
    return ensure_text(edited_text, source_name="编辑器")


def resolve_input_text(
    *,
    ctx: typer.Context,
    source: str | None = None,
    clip: bool = False,
    edit: bool = False,
) -> str:
    if clip:
        return load_text_from_clipboard()

    if edit:
        return load_text_from_editor()

    if source == "-":
        return load_text_from_stdin()

    if source is not None:
        return load_text_from_file(source)

    if not sys.stdin.isatty():
        return load_text_from_stdin()

    abort(
        "未提供任何输入。请提供文件、管道输入、`-`、`--clip` 或 `--edit`。",
        code=2,
        ctx=ctx,
        show_help=True,
    )
