from __future__ import annotations

from pathlib import Path

from word_book.core.config import discover_config_files, load_app_config




def _write_config(config_dir: Path, *, main_book_path: str) -> None:
    safe_main_book_path = main_book_path.replace("\\", "\\\\")
    config_dir.mkdir(parents=True, exist_ok=True)
    _ = (config_dir / "config.toml").write_text(
        '\n'.join(
            [
                'title = "My Word Book"',
                '[settings]',
                f'main_book_path = "{safe_main_book_path}"',
            ]
        ),
        encoding="utf-8",
    )

    _ = (config_dir / "config.env").write_text(
        'API_KEY="k"\nLLM_BASE_URL="https://example.test"\nLLM_MODEL="m"\n',
        encoding="utf-8",
    )


def test_discover_home_config_as_global_when_running_in_home(tmp_path: Path) -> None:

    home_dir = tmp_path / "home"
    home_dir.mkdir()
    _write_config(home_dir / ".bookconfig", main_book_path=str(home_dir / "word_book.md"))

    source, config_dir, _, _ = discover_config_files(start_dir=home_dir, home_dir=home_dir)


    assert source == "global"
    assert config_dir == home_dir / ".bookconfig"


def test_discover_prefers_project_config_over_global(tmp_path: Path) -> None:

    home_dir = tmp_path / "home"
    project_dir = home_dir / "workspace" / "project"
    project_dir.mkdir(parents=True)

    _write_config(home_dir / ".bookconfig", main_book_path=str(home_dir / "word_book.md"))
    _write_config(project_dir / ".bookconfig", main_book_path="word_book.md")

    source, config_dir, _, _ = discover_config_files(start_dir=project_dir, home_dir=home_dir)



    assert source == "project"
    assert config_dir == project_dir / ".bookconfig"


def test_load_app_config_sets_working_dir_to_main_book_parent_for_project(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    target_dir = tmp_path / "books"
    target_dir.mkdir()

    _write_config(project_dir / ".bookconfig", main_book_path=str(target_dir / "custom.md"))

    config = load_app_config(start_dir=project_dir)

    assert config.config_source == "project"
    assert config.main_book_path == (target_dir / "custom.md").resolve()
    assert config.working_dir == config.main_book_path.parent
