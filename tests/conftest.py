from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from word_book.core.config import AppConfig, Settings  # noqa: E402


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def make_config(tmp_path: Path) -> Callable[..., AppConfig]:
    def _make_config(
        *,
        main_book_path: Path | None = None,
        working_dir: Path | None = None,
        env_config: dict[str, str | None] | None = None,
    ) -> AppConfig:
        resolved_working_dir = working_dir or tmp_path
        resolved_main_book_path = main_book_path or resolved_working_dir / "word_book.md"
        return AppConfig(
            config_dir=resolved_working_dir / ".bookconfig",
            working_dir=resolved_working_dir,
            main_book_path=resolved_main_book_path,
            toml_config=Settings(main_book_path=str(resolved_main_book_path)),
            env_config=env_config
            if env_config is not None
            else {
                "API_KEY": "test-key",
                "LLM_BASE_URL": "https://llm.example.test",
                "LLM_MODEL": "test-model",
            },
            config_source="project",
        )

    return _make_config


@pytest.fixture
def make_ctx(make_config: Callable[..., AppConfig]) -> Callable[..., SimpleNamespace]:
    def _make_ctx(**config_kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(obj=make_config(**config_kwargs))

    return _make_ctx
