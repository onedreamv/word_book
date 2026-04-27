from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import dotenv_values
import tomllib


ConfigSource = Literal["project", "global"]


# 定义数据类，用于存储配置信息
# toml 文件未来可能添加多种数值类型，嵌套 dataclass 以便安全处理数值类型，并且利好 IDE 类型注解
@dataclass(frozen=True)
class Settings:
    main_book_path: str


@dataclass(frozen=True)
class AppConfig:
    config_dir: Path
    working_dir: Path
    main_book_path: Path
    toml_config: Settings
    env_config: dict[str, str | None]
    config_source: ConfigSource


class ConfigError(Exception):
    """配置加载相关异常。"""


class NotFoundConfigDirError(ConfigError):
    """未找到 project/global 配置目录。"""


class InvalidConfigError(ConfigError):
    """配置文件存在但内容或路径非法。"""


# 定义常量
CONFIG_DIR_NAME = ".bookconfig"
TOML_CONFIG_FILE_NAME = "config.toml"
ENV_CONFIG_FILE_NAME = "config.env"


def _get_config_file_paths(config_dir: Path) -> tuple[Path, Path]:
    """检查toml 和 env 文件是否存在"""
    toml_path = config_dir / TOML_CONFIG_FILE_NAME
    env_path = config_dir / ENV_CONFIG_FILE_NAME
    return toml_path, env_path


def _ensure_complete_config_dir(config_dir: Path, *, source_label: str) -> tuple[Path, Path]:
    """确认项目或全局配置目录完整,不完整则抛出错误"""
    if not config_dir.is_dir():
        raise InvalidConfigError(f"{source_label} 配置路径 `{config_dir}` 不是目录。")

    toml_path, env_path = _get_config_file_paths(config_dir)
    missing_files: list[str] = []

    if not toml_path.exists():
        missing_files.append(TOML_CONFIG_FILE_NAME)
    if not env_path.exists():
        missing_files.append(ENV_CONFIG_FILE_NAME)

    if missing_files:
        missing_text = "、".join(f"`{file_name}`" for file_name in missing_files)
        raise InvalidConfigError(f"{source_label} 配置目录 `{config_dir}` 缺少 {missing_text}。")

    return toml_path, env_path

def discover_config_files(start_dir: Path | None = None) -> tuple[ConfigSource, Path, Path, Path]:
    """优先向上递归查找 project config，找不到时回退到 global config。"""
    current_dir = (start_dir or Path.cwd()).resolve()
     # 优先使用当前目录,递归向上搜索
    for search_dir in (current_dir, *current_dir.parents):
        config_dir = search_dir / CONFIG_DIR_NAME
        if not config_dir.exists():
            continue

        toml_path, env_path = _ensure_complete_config_dir(config_dir, source_label="project")
        return "project", config_dir, toml_path, env_path

    global_config_dir = Path.home() / CONFIG_DIR_NAME
    if global_config_dir.exists():
        toml_path, env_path = _ensure_complete_config_dir(global_config_dir, source_label="global")
        return "global", global_config_dir, toml_path, env_path

    raise NotFoundConfigDirError(
        "未找到可用配置。请运行 `word_book init` 创建 project 配置，或运行 `word_book init --global` 创建全局配置。"
    )


def _load_settings(toml_path: Path) -> Settings:
    """加载 TOML 配置文件"""
    try:
        with toml_path.open("rb") as file:
            toml_data = tomllib.load(file)
    except tomllib.TOMLDecodeError as exc:
        raise InvalidConfigError(f"读取 TOML 配置文件 `{toml_path}` 失败: {exc}") from exc
    except OSError as exc:
        raise InvalidConfigError(f"读取 TOML 配置文件 `{toml_path}` 失败: {exc}") from exc

    settings_obj = toml_data.get("settings")
    if not isinstance(settings_obj, dict):
        raise InvalidConfigError(f"配置文件 `{toml_path}` 缺少有效的 `[settings]` 段。")

    raw_main_book_path = settings_obj.get("main_book_path")
    if not isinstance(raw_main_book_path, str) or not raw_main_book_path.strip():
        raise InvalidConfigError(f"配置文件 `{toml_path}` 中的 `settings.main_book_path` 必须是非空字符串。")

    return Settings(main_book_path=raw_main_book_path.strip())


def _load_env_config(env_path: Path) -> dict[str, str | None]:
    """加载环境配置文件"""
    try:
        return dict(dotenv_values(env_path))
    except OSError as exc:
        raise InvalidConfigError(f"读取环境配置文件 `{env_path}` 失败: {exc}") from exc


def _resolve_main_book_path(*, settings: Settings, config_dir: Path, config_source: ConfigSource) -> tuple[Path, Path]:
    """解析主词书路径,区分项目和全局配置.检查工作目录是否存在,返回工作目录和主词书路径。"""
    raw_main_book_path = Path(settings.main_book_path)


    if config_source == "project":
        working_dir = config_dir.parent.resolve()
        main_book_path = raw_main_book_path if raw_main_book_path.is_absolute() else working_dir / raw_main_book_path
    else:
        if not raw_main_book_path.is_absolute():
            raise InvalidConfigError(
                "global 配置中的 `main_book_path` 必须是绝对路径。请修改配置后重试，或运行 `word_book init --global` 重新初始化。"
            )
        main_book_path = raw_main_book_path
        working_dir = main_book_path.parent.resolve()

    resolved_main_book_path = main_book_path.resolve(strict=False)

    if not working_dir.exists():
        raise InvalidConfigError(
            f"默认词书目录 `{working_dir}` 不存在。请先创建该目录，或修正 `main_book_path`。"
        )
    if not working_dir.is_dir():
        raise InvalidConfigError(f"默认词书目录 `{working_dir}` 不是目录。")
    if resolved_main_book_path.exists() and not resolved_main_book_path.is_file():
        raise InvalidConfigError(f"默认词书路径 `{resolved_main_book_path}` 不是文件。")

    return working_dir, resolved_main_book_path


def load_app_config(start_dir: Path | None = None) -> AppConfig:
    """加载并返回运行期可直接使用的应用配置。"""
    config_source, config_dir, toml_path, env_path = discover_config_files(start_dir=start_dir)
    settings = _load_settings(toml_path)
    env_config = _load_env_config(env_path)
    working_dir, main_book_path = _resolve_main_book_path(
        settings=settings,
        config_dir=config_dir,
        config_source=config_source,
    )

    return AppConfig(
        config_dir=config_dir,
        working_dir=working_dir,
        main_book_path=main_book_path,
        toml_config=settings,
        env_config=env_config,
        config_source=config_source,
    )
