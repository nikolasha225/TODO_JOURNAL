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

