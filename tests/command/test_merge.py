from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import cast, override

import pytest
import typer

from word_book.command.merge import merge


def _ctx_with_obj(obj: object | None = None) -> typer.Context:
    return cast(typer.Context, cast(object, SimpleNamespace(obj=obj)))



def test_merge_appends_only_new_words_to_specified_main_book(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    main_book = tmp_path / "main.md"
    other_book = tmp_path / "other.md"
    _ = main_book.write_text("apple", encoding="utf-8")
    _ = other_book.write_text("apple\nbanana\ncarrot\n", encoding="utf-8")

    merge(_ctx_with_obj(), other_book_path=other_book, main_book_path=main_book)

    lines = main_book.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "apple"
    assert set(lines[1:]) == {"banana", "carrot"}
    assert "已合并 2 个新单词" in capsys.readouterr().out


def test_merge_prints_noop_when_no_new_words(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    main_book = tmp_path / "main.md"
    other_book = tmp_path / "other.md"
    _ = main_book.write_text("apple\nbanana\n", encoding="utf-8")
    _ = other_book.write_text("apple\nbanana\n", encoding="utf-8")

    merge(_ctx_with_obj(), other_book_path=other_book, main_book_path=main_book)

    assert main_book.read_text(encoding="utf-8") == "apple\nbanana\n"
    assert "没有新单词需要合并" in capsys.readouterr().out


def test_merge_uses_default_main_book_from_context(
    make_ctx: Callable[..., object],
    tmp_path: Path,
) -> None:
    main_book = tmp_path / "default.md"
    other_book = tmp_path / "other.md"
    _ = main_book.write_text("apple\n", encoding="utf-8")
    _ = other_book.write_text("dragon\n", encoding="utf-8")

    merge(cast(typer.Context, make_ctx(main_book_path=main_book)), other_book_path=other_book, main_book_path=None)

    assert main_book.read_text(encoding="utf-8").splitlines() == ["apple", "dragon"]


@pytest.mark.parametrize(
    ("main_exists", "other_exists"),
    [
        (False, True),
        (True, False),
    ],
)
def test_merge_rejects_missing_books(tmp_path: Path, main_exists: bool, other_exists: bool) -> None:
    main_book = tmp_path / "main.md"
    other_book = tmp_path / "other.md"
    if main_exists:
        _ = main_book.write_text("apple\n", encoding="utf-8")
    if other_exists:
        _ = other_book.write_text("banana\n", encoding="utf-8")

    with pytest.raises(typer.Exit) as exc_info:
        merge(_ctx_with_obj(), other_book_path=other_book, main_book_path=main_book)

    assert exc_info.value.exit_code == 1


@pytest.mark.parametrize("main_is_directory", [True, False])
def test_merge_rejects_directory_paths(tmp_path: Path, main_is_directory: bool) -> None:
    main_book = tmp_path / "main"
    other_book = tmp_path / "other"
    if main_is_directory:
        main_book.mkdir()
        _ = other_book.write_text("banana\n", encoding="utf-8")
    else:
        _ = main_book.write_text("apple\n", encoding="utf-8")
        other_book.mkdir()

    with pytest.raises(typer.Exit) as exc_info:
        merge(_ctx_with_obj(), other_book_path=other_book, main_book_path=main_book)

    assert exc_info.value.exit_code == 1


class UnreadableBook:
    def exists(self) -> bool:
        return True

    def is_file(self) -> bool:
        return True

    def open(self, *_args: object, **_kwargs: object) -> object:
        raise OSError("cannot read")

    @override
    def __str__(self) -> str:
        return "unreadable-book"


def test_merge_aborts_when_a_book_cannot_be_read(tmp_path: Path) -> None:
    other_book = tmp_path / "other.md"
    _ = other_book.write_text("banana\n", encoding="utf-8")

    with pytest.raises(typer.Exit) as exc_info:
        merge(_ctx_with_obj(), other_book_path=other_book, main_book_path=cast(Path, cast(object, UnreadableBook())))


    assert exc_info.value.exit_code == 1

