from pathlib import Path
from dataclasses import dataclass

# 定义数据类，用于存储配置信息
# toml文件未来可能添加多种数值类型,嵌套dataclass以便安全处理数值类型,并且利好IDE类型注解
@dataclass(frozen=True)
class Settings:
    main_book_path: str

@dataclass(frozen=True)
class AppConfig:
    config_dir: Path
    toml_config: Settings
    env_config: dict[str, str | None]

# 定义找不到配置目录的异常
class NotFoundConfigDirError(Exception):
    pass

# 定义常量
CONFIG_DIR_NAME = ".bookconfig"
TOML_CONFIG_FILE_NAME = "config.toml"
ENV_CONFIG_FILE_NAME = "config.env"

# 获取,检查,返回配置目录,配置文件路径
def get_config_dir() -> tuple[Path,Path,Path]:
    """获取配置目录"""
    config_dir = Path.cwd() / CONFIG_DIR_NAME
    toml_path = config_dir / TOML_CONFIG_FILE_NAME
    env_path = config_dir / ENV_CONFIG_FILE_NAME

    if config_dir.exists() and (toml_path.exists() and env_path.exists()):
        return config_dir,toml_path,env_path
    else:
        raise NotFoundConfigDirError
    
