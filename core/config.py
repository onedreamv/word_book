from pathlib import Path

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
    
