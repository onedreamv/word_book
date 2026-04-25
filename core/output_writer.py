from collections.abc import Iterable
from pathlib import Path
from .exceptions import abort

def resolve_unique_path(base_dir: Path, name: str, extension: str) -> Path:
    """解决同名文件冲突，生成唯一的文件路径"""
    output_path = base_dir / f"{name}{extension}"
    if not output_path.exists():
        return output_path

    index = 1
    while True:
        output_path = base_dir / f"{name}{index}{extension}"
        if not output_path.exists():
            return output_path
        index += 1

def write_lines_to_file(lines: Iterable[str], output_path: Path) -> Path:
    """将字符串列表按行写入文件"""
    content = "".join(f"{line}\n" for line in lines if line.strip())
    try:
        _ = output_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        abort(f"写入输出文件失败: {output_path} ({exc})")

    return output_path

def append_lines_to_file(lines: Iterable[str], output_path: Path) -> Path:
    """将字符串列表按行追加到文件"""
    content = "".join(f"{line}\n" for line in lines if line.strip())
    if not content:
        return output_path
        
    try:
        with output_path.open("a", encoding="utf-8") as file:
            _ = file.write(content)
    except OSError as exc:
        abort(f"追加写入文件失败: {output_path} ({exc})")

    return output_path

