#Работа с когфиг файлом

import os
import sys
import yaml
from typing import Any, Dict, Optional

from src.exceptions import TodoJournalError


# Константы
APP_NAME = "todo"
CONFIG_FILENAME = "config.yaml"


#Возвращает путь к кфг КАТАЛОГУ
    #Windows -> %APPDATA%\\tod o "(туду вместе писать нельзя иначе не коммитится)
    #Unix -> ~/.config/tod o
def get_config_directory() -> str:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", "")
        if not base:
            raise TodoJournalError("ConfigNotFound", config_path="Unknown")
        config_dir = os.path.join(base, APP_NAME)
    else:
        config_dir = os.path.join(os.path.expanduser("~"), ".config", APP_NAME)

    #аля touch
    try:
        os.makedirs(config_dir, exist_ok=True)
    except OSError as e:
        raise TodoJournalError("ConfigDirectoryIsFile",
                               config_directory_path=config_dir) from e
    return config_dir


#Возвращает полный путь к кфг ФАЙЛУ
def get_config_path() -> str:
    config_dir = get_config_directory()
    return os.path.join(config_dir, CONFIG_FILENAME)


#Загружает конфигурацию из config.yaml + touch
def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    if config_path is None:
        config_path = get_config_path()

    if not os.path.exists(config_path):
        # Создаём конфиг по умолчанию
        default_config = {
            "current_journal": None,
            "journals": {},   # имя -> путь
            "editor": "notepad" if sys.platform == "win32" else "nano",
        }
        save_config(default_config, config_path)
        return default_config

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except (yaml.YAMLError, OSError) as e:
        raise TodoJournalError("ConfigNotFound",
                               config_path=config_path) from e

    # Гарантируем наличие необходимых полей
    if "journals" not in config:
        config["journals"] = {}
    if "current_journal" not in config:
        config["current_journal"] = None
    if "editor" not in config:
        config["editor"] = "notepad" if sys.platform == "win32" else "nano"

    return config


#Сохраняет конфигурацию в config.yaml
def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    if config_path is None:
        config_path = get_config_path()

    # Убедимся, что каталог существует
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)