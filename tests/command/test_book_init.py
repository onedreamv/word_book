from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner


from word_book.cli import app
from word_book.command import book_init


def test_build_default_toml_uses_requested_main_book_path() -> None:
    content = book_init.build_default_toml("words/custom.md")

    assert 'title = "My Word Book"' in content
    assert 'main_book_path = "words/custom.md"' in content


def test_get_init_paths_for_project_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:

    monkeypatch.chdir(tmp_path)

    config_dir, toml_file, env_file, default_main_book_path = book_init.get_init_paths(False)

    assert config_dir == tmp_path / ".bookconfig"
    assert toml_file == config_dir / "config.toml"
    assert env_file == config_dir / "config.env"
    assert default_main_book_path == "word_book.md"


def test_init_creates_project_config_files(runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:

    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert (tmp_path / ".bookconfig" / "config.toml").read_text(encoding="utf-8") == book_init.build_default_toml("word_book.md")
    assert (tmp_path / ".bookconfig" / "config.env").read_text(encoding="utf-8") == book_init.DEFAULT_ENV
    assert "初始化成功" in result.output


def test_init_creates_global_config_files(runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))


    result = runner.invoke(app, ["init", "--global"])

    expected_book = str((tmp_path / "word_book.md").resolve())
    config_dir = tmp_path / ".bookconfig"
    assert result.exit_code == 0
    assert (config_dir / "config.toml").read_text(encoding="utf-8") == book_init.build_default_toml(expected_book)
    assert (config_dir / "config.env").read_text(encoding="utf-8") == book_init.DEFAULT_ENV


def test_init_rejects_project_and_global_together(runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:

    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init", "--project", "--global"])

    assert result.exit_code == 1
    assert "不能同时使用" in result.output
    assert not (tmp_path / ".bookconfig").exists()


def test_init_rejects_existing_config_without_force(runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    config_dir = tmp_path / ".bookconfig"
    config_dir.mkdir()
    _ = (config_dir / "config.toml").write_text("old", encoding="utf-8")


    result = runner.invoke(app, ["init"])

    assert result.exit_code == 1
    assert "已存在" in result.output
    assert (config_dir / "config.toml").read_text(encoding="utf-8") == "old"


def test_init_force_overwrites_existing_config(runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:

    monkeypatch.chdir(tmp_path)
    config_dir = tmp_path / ".bookconfig"
    config_dir.mkdir()
    _ = (config_dir / "config.toml").write_text("old toml", encoding="utf-8")

    _ = (config_dir / "config.env").write_text("old env", encoding="utf-8")


    result = runner.invoke(app, ["init", "--force"])

    assert result.exit_code == 0
    assert (config_dir / "config.toml").read_text(encoding="utf-8") == book_init.build_default_toml("word_book.md")
    assert (config_dir / "config.env").read_text(encoding="utf-8") == book_init.DEFAULT_ENV
    assert "覆盖写入" in result.output


def test_init_rejects_config_path_that_is_file(runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    _ = (tmp_path / ".bookconfig").write_text("not a directory", encoding="utf-8")


    result = runner.invoke(app, ["init"])

    assert result.exit_code == 1
    assert "不是目录" in result.output
