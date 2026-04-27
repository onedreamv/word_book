"""兼容入口：支持 `uv run python cli.py ...` 调用包内 CLI。"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from word_book.cli import app


if __name__ == "__main__":
    app()

