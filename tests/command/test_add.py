from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import cast



import pytest
import typer

from word_book.command.add import add


def make_typing_ctx(obj: object | None = None) -> typer.Context:
    """为类型检查构造与 `typer.Context` 兼容的测试上下文。"""
    return cast(typer.Context, cast(object, SimpleNamespace(obj=obj)))



def test_add_appends_new_word_to_specified_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    book_path = tmp_path / "book.md"
    _ = book_path.write_text("apple", encoding="utf-8")

    add(make_typing_ctx(), "banana", book_path=book_path)

    assert book_path.read_text(encoding="utf-8") == "apple\nbanana\n"
    assert "banana" in capsys.readouterr().out


def test_add_skips_duplicate_word(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    book_path = tmp_path / "book.md"
    _ = book_path.write_text("apple\nbanana\n", encoding="utf-8")

    add(make_typing_ctx(), "banana", book_path=book_path)

    assert book_path.read_text(encoding="utf-8") == "apple\nbanana\n"
    assert "已经在词书里" in capsys.readouterr().out


def test_add_uses_default_book_from_context(
    make_ctx: Callable[..., typer.Context], tmp_path: Path
) -> None:
    book_path = tmp_path / "default.md"
    _ = book_path.write_text("", encoding="utf-8")

    add(make_ctx(main_book_path=book_path), "contextual", book_path=None)


    assert book_path.read_text(encoding="utf-8") == "contextual\n"


def test_add_rejects_missing_book(tmp_path: Path) -> None:
    with pytest.raises(typer.Exit) as exc_info:
        add(make_typing_ctx(), "banana", book_path=tmp_path / "missing.md")

    assert exc_info.value.exit_code == 1


def test_add_rejects_directory_book_path(tmp_path: Path) -> None:
    with pytest.raises(typer.Exit) as exc_info:
        add(make_typing_ctx(), "banana", book_path=tmp_path)

    assert exc_info.value.exit_code == 1


def test_add_aborts_when_book_cannot_be_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    book_path = tmp_path / "book.md"
    _ = book_path.write_text("banana\n", encoding="utf-8")

    def raise_oserror(*_args: object, **_kwargs: object) -> object:
        raise OSError("cannot read")

    monkeypatch.setattr(Path, "open", raise_oserror)

    with pytest.raises(typer.Exit) as exc_info:
        add(make_typing_ctx(), "banana", book_path=book_path)

    assert exc_info.value.exit_code == 1


