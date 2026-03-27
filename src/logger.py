import logging
import logging.config
import os
import sys

#Настройка логирования из кфг файла
def setup_logging(config_path: str = "logging.ini"):
    if os.path.exists(config_path):
        logging.config.fileConfig(config_path)
    else:
        # Если файла нет, используем базовую конфигурацию
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        logging.warning(f"Конфигурация логирования {config_path} не найдена, используется базовая")

#Возвращает логгер с заданным именем
def get_logger(name: str = "todo") -> logging.Logger:
    return logging.getLogger(name)