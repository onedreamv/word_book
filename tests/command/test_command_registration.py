from __future__ import annotations

from typer.testing import CliRunner

from word_book.cli import app


def test_top_level_help_lists_registered_commands(runner: CliRunner) -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    for command_name in ("init", "add", "clean", "merge"):
        assert command_name in result.output


def test_version_option_prints_version_and_exits(runner: CliRunner) -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
