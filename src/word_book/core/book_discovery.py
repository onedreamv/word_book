from pathlib import Path

from .config import AppConfig
from .exceptions import abort


def ensure_book_file(path: Path, *, label: str) -> Path:
    resolved_path = path.resolve(strict=False)
    if not resolved_path.exists():
        abort(f"{label} `{resolved_path}` 不存在。")
    if not resolved_path.is_file():
        abort(f"{label} `{resolved_path}` 不是文件。")
    return resolved_path


def discover_book_path(user_input_path: Path, config: AppConfig) -> Path:
    """发现并校验用户显式指定的词书路径，返回绝对路径。"""
    expanded_path = user_input_path.expanduser()

    if expanded_path.is_absolute():
        return ensure_book_file(expanded_path, label="词书")

    current_dir_candidate = expanded_path.resolve(strict=False)
    if current_dir_candidate.exists():
        return ensure_book_file(current_dir_candidate, label="词书")

    working_dir_candidate = (config.working_dir / expanded_path).resolve(strict=False)
    if working_dir_candidate.exists():
        return ensure_book_file(working_dir_candidate, label="词书")

    abort(
        f"词书 `{user_input_path}` 不存在。已搜索: `{current_dir_candidate}`、`{working_dir_candidate}`。"
    )
