#Тесты для  config

import os
import pytest
import yaml
from src import config
from src.exceptions import TodoJournalError


#Подмена os.makedirs на заглушку
@pytest.fixture
def mock_makedirs(monkeypatch):
    def fake_makedirs(path, exist_ok=False):
        pass
    monkeypatch.setattr(os, "makedirs", fake_makedirs)


# Проверка пути к каталогу (используем mock_makedirs)
def test_get_config_directory(monkeypatch, mock_makedirs):
    #Типо Windows
    monkeypatch.setattr("sys.platform", "win32")
    monkeypatch.setenv("APPDATA", "C:\\Users\\Test\\AppData\\Roaming")
    dir_win = config.get_config_directory()
    # Используем os.path.normpath для приведения к единому формату
    assert os.path.normpath(dir_win) == os.path.normpath("C:\\Users\\Test\\AppData\\Roaming\\todo")

    #Типо Unix
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setenv("HOME", "/home/test")
    dir_unix = config.get_config_directory()
    assert os.path.normpath(dir_unix) == os.path.normpath("/home/test/.config/todo")


def test_get_config_path(monkeypatch, mock_makedirs):
    #Unix
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setattr(os.path, "expanduser", lambda x: "/home/test")
    path = config.get_config_path()
    #Проверяем, что путь заканчивается на config.yaml и содержит компоненты
    assert path.endswith("config.yaml")
    assert ".config/todo" in path or ".config\\todo" in path  # поддерживаем оба варианта
    assert "/home/test" in path or "\\home\\test" in path

    #Windows
    monkeypatch.setattr("sys.platform", "win32")
    monkeypatch.setenv("APPDATA", "C:\\Users\\Test\\AppData\\Roaming")
    path = config.get_config_path()
    assert path.endswith("config.yaml")
    assert "todo" in path
    assert "AppData\\Roaming" in path or "AppData/Roaming" in path


#Если конфига нет, он должен быть создан с настройками по умолчанию
def test_load_config_creates_default(tmpdir, monkeypatch):
    # Подменяем get_config_path, чтобы использовать tmpdir
    def mock_get_config_path():
        return str(tmpdir.join(config.CONFIG_FILENAME))
    monkeypatch.setattr(config, "get_config_path", mock_get_config_path)

    cfg = config.load_config()
    assert cfg["current_journal"] is None
    assert cfg["journals"] == {}
    assert cfg["editor"] in ("notepad", "nano")  # зависит от ОС

    # Проверяем, что файл действительно создан
    assert os.path.exists(tmpdir.join(config.CONFIG_FILENAME))


#Загрузка существующего корректного конфига
def test_load_config_existing(tmpdir, monkeypatch):
    config_path = tmpdir.join(config.CONFIG_FILENAME)
    test_data = {
        "current_journal": "work",
        "journals": {"work": "/path/to/work.todo", "home": "/path/to/home.todo"},
        "editor": "vim"
    }
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(test_data, f)

    def mock_get_config_path():
        return str(config_path)
    monkeypatch.setattr(config, "get_config_path", mock_get_config_path)

    cfg = config.load_config()
    assert cfg == test_data


#Кривой YAML -> исключение
def test_load_config_broken_yaml(tmpdir, monkeypatch):
    config_path = tmpdir.join(config.CONFIG_FILENAME)
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write("invalid: yaml: [")
    def mock_get_config_path():
        return str(config_path)
    monkeypatch.setattr(config, "get_config_path", mock_get_config_path)

    with pytest.raises(TodoJournalError, match="Конфигурационный файл не найден"):
        config.load_config()


#Сохранение конфиг
def test_save_config(tmpdir, monkeypatch):
    config_path = tmpdir.join("custom.yaml")
    data = {"key": "value"}
    config.save_config(data, config_path)
    assert os.path.exists(config_path)
    with open(config_path, 'r', encoding='utf-8') as f:
        loaded = yaml.safe_load(f)
    assert loaded == data