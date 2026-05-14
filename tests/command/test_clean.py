from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import cast


import pytest
import typer
import word_book.command.clean as clean_module

MakeCtx = Callable[..., SimpleNamespace]


class FakeLLMClient:

    def __init__(self, response: str):
        self.response: str = response
        self.calls: list[dict[str, object]] = []


    def chat(self, system_prompt: str, user_prompt: str, response_format: dict[str, object] | None = None) -> str:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "response_format": response_format,
            }
        )
        return self.response


def test_word_extractor_calls_llm_and_parses_words() -> None:
    llm = FakeLLMClient('{"words": [" developer ", "", "initialize"]}')
    extractor = clean_module.WordExtractor(llm_client=llm)

    words = extractor.extract("dev init")

    assert words == ["developer", "initialize"]
    assert len(llm.calls) == 1
    assert "dev init" in str(llm.calls[0]["user_prompt"])
    assert llm.calls[0]["response_format"] == {"type": "json_object"}


@pytest.mark.parametrize(
    "payload",
    [
        "not json",
        "[]",
        "{}",
        '{"words": "developer"}',
        '{"words": ["developer", 123]}',
    ],
)
def test_word_extractor_aborts_on_invalid_llm_payloads(payload: str) -> None:
    extractor = clean_module.WordExtractor(llm_client=FakeLLMClient(payload))

    with pytest.raises(typer.Exit) as exc_info:
        _ = extractor.extract("text")


    assert exc_info.value.exit_code == 1


def test_build_output_preview_for_short_list() -> None:
    assert clean_module.build_output_preview(["one", "two"]) == "one\ntwo"


def test_build_output_preview_truncates_long_list() -> None:
    words = [f"word{i}" for i in range(12)]

    preview = clean_module.build_output_preview(words)

    assert preview.splitlines() == [*words[:10], "10+ words more..."]


def test_clean_writes_extracted_words_without_external_services(
    monkeypatch: pytest.MonkeyPatch,
    make_ctx: MakeCtx,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    captured_init: dict[str, str | None] = {}

    def fake_resolve_input_text(
        *,
        ctx: typer.Context,
        source: str | None = None,
        clip: bool = False,
        edit: bool = False,
    ) -> str:
        _ = ctx
        assert source == "input.txt"
        assert clip is True
        assert edit is False
        return "raw input"

    class FakeOpenAIClient:
        def __init__(self, api_key: str, base_url: str, model: str):
            captured_init.update({"api_key": api_key, "base_url": base_url, "model": model})

        def chat(self, system_prompt: str, user_prompt: str, response_format: dict[str, object] | None = None) -> str:
            assert "raw input" in user_prompt
            assert response_format == {"type": "json_object"}
            return '{"words": ["alpha", "beta"]}'

    monkeypatch.setattr(clean_module, "resolve_input_text", fake_resolve_input_text)
    monkeypatch.setattr(clean_module, "OpenAIClient", FakeOpenAIClient)

    clean_module.clean(
        cast(typer.Context, cast(object, make_ctx(working_dir=tmp_path))),
        source="input.txt",
        clip=True,
        edit=False,
    )


    assert captured_init == {
        "api_key": "test-key",
        "base_url": "https://llm.example.test",
        "model": "test-model",
    }
    assert (tmp_path / "cleaned.txt").read_text(encoding="utf-8") == "alpha\nbeta\n"
    output = capsys.readouterr().out
    assert "已清理并写入了 2 个单词" in output
    assert "alpha" in output
    assert "beta" in output


def test_clean_uses_unique_output_path(monkeypatch: pytest.MonkeyPatch, make_ctx: MakeCtx, tmp_path: Path) -> None:
    _ = (tmp_path / "cleaned.txt").write_text("existing\n", encoding="utf-8")

    class FakeOpenAIClient:
        def __init__(self, api_key: str, base_url: str, model: str):
            pass

        def chat(self, system_prompt: str, user_prompt: str, response_format: dict[str, object] | None = None) -> str:
            return '{"words": ["gamma"]}'

    def fake_resolve_input_text(**_kwargs: object) -> str:
        return "raw input"

    monkeypatch.setattr(clean_module, "resolve_input_text", fake_resolve_input_text)
    monkeypatch.setattr(clean_module, "OpenAIClient", FakeOpenAIClient)


    clean_module.clean(
        cast(typer.Context, cast(object, make_ctx(working_dir=tmp_path))),
        source=None,
        clip=False,
        edit=False,
    )


    assert (tmp_path / "cleaned.txt").read_text(encoding="utf-8") == "existing\n"
    assert (tmp_path / "cleaned1.txt").read_text(encoding="utf-8") == "gamma\n"


@pytest.mark.parametrize(
    "env_config",
    [
        {"API_KEY": None, "LLM_BASE_URL": "https://llm.example.test", "LLM_MODEL": "test-model"},
        {"API_KEY": "test-key", "LLM_BASE_URL": None, "LLM_MODEL": "test-model"},
        {"API_KEY": "test-key", "LLM_BASE_URL": "https://llm.example.test", "LLM_MODEL": None},
    ],
)
def test_clean_aborts_when_required_env_config_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    make_ctx: MakeCtx,
    tmp_path: Path,
    env_config: dict[str, str | None],
) -> None:
    def fake_resolve_input_text(**_kwargs: object) -> str:
        return "raw input"

    monkeypatch.setattr(clean_module, "resolve_input_text", fake_resolve_input_text)


    with pytest.raises(typer.Exit) as exc_info:
        clean_module.clean(
            cast(typer.Context, cast(object, make_ctx(working_dir=tmp_path, env_config=env_config))),
            source=None,
            clip=False,
            edit=False,
        )


    assert exc_info.value.exit_code == 1
