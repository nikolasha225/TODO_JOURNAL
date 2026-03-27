import logging
import tempfile
import os
import pytest
from src.logger import setup_logging, get_logger

#тесты логгера

def test_setup_logging():
    # Создаём временный конфигурационный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write("""
[loggers]
keys=root

[handlers]
keys=consoleHandler

[formatters]
keys=consoleFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler

[handler_consoleHandler]
class=logging.StreamHandler
level=DEBUG
formatter=consoleFormatter
args=(sys.stdout,)

[formatter_consoleFormatter]
class=logging.Formatter
format=%(message)s
""")
        config_path = f.name

    # Сохраняем текущие логгеры и обработчики, чтобы восстановить после теста
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level

    try:
        setup_logging(config_path)
        # После настройки уровень root логгера должен быть DEBUG
        assert root_logger.level == logging.DEBUG
        # Проверяем, что есть хотя бы один обработчик
        assert len(root_logger.handlers) >= 1
        # Проверяем, что обработчик имеет тип StreamHandler
        assert any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
    finally:
        # Восстанавливаем исходное состояние
        root_logger.handlers = original_handlers
        root_logger.setLevel(original_level)
        os.unlink(config_path)

def test_get_logger():
    logger = get_logger("test_logger")
    assert logger.name == "test_logger"