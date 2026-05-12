from pathlib import Path
from typing import Callable

import pytest
import typer

from word_book.core.config import AppConfig
from word_book.core.book_discovery import discover_book_path


def test_discover_returns_absolute_path_for_absolute_input(
    make_config: Callable[..., AppConfig],
    tmp_path: Path,
) -> None:
    book_path = tmp_path / "book.md"
    _ = book_path.write_text("apple\n", encoding="utf-8")

    assert discover_book_path(book_path, make_config()) == book_path.resolve()


def test_discover_prefers_current_directory_for_relative_input(
    make_config: Callable[..., AppConfig],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_dir = tmp_path / "current"
    working_dir = tmp_path / "working"
    current_dir.mkdir()
    working_dir.mkdir()
    current_book = current_dir / "buffer.txt"
    working_book = working_dir / "buffer.txt"
    _ = current_book.write_text("current\n", encoding="utf-8")
    _ = working_book.write_text("working\n", encoding="utf-8")
    monkeypatch.chdir(current_dir)

    result = discover_book_path(Path("buffer.txt"), make_config(working_dir=working_dir))

    assert result == current_book.resolve()


def test_discover_falls_back_to_working_dir_for_relative_input(
    make_config: Callable[..., AppConfig],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_dir = tmp_path / "current"
    working_dir = tmp_path / "working"
    current_dir.mkdir()
    working_dir.mkdir()
    working_book = working_dir / "buffer.txt"
    _ = working_book.write_text("working\n", encoding="utf-8")
    monkeypatch.chdir(current_dir)

    result = discover_book_path(Path("buffer.txt"), make_config(working_dir=working_dir))

    assert result == working_book.resolve()


def test_discover_absolute_missing_path_does_not_fallback_to_working_dir(
    make_config: Callable[..., AppConfig],
    tmp_path: Path,
) -> None:
    working_dir = tmp_path / "working"
    missing_dir = tmp_path / "missing"
    working_dir.mkdir()
    missing_dir.mkdir()
    _ = (working_dir / "buffer.txt").write_text("working\n", encoding="utf-8")

    with pytest.raises(typer.Exit) as exc_info:
        discover_book_path(missing_dir / "buffer.txt", make_config(working_dir=working_dir))

    assert exc_info.value.exit_code == 1


def test_discover_rejects_directory_candidate(
    make_config: Callable[..., AppConfig],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current_dir = tmp_path / "current"
    working_dir = tmp_path / "working"
    current_dir.mkdir()
    working_dir.mkdir()
    (current_dir / "buffer.txt").mkdir()
    monkeypatch.chdir(current_dir)

    with pytest.raises(typer.Exit) as exc_info:
        discover_book_path(Path("buffer.txt"), make_config(working_dir=working_dir))

    assert exc_info.value.exit_code == 1
