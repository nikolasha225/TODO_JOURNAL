"""Модуль для работы с todo-журналом."""

import json
import sys
from typing import Dict, List, Union, NoReturn


class TodoJournalError(Exception):
    """Базовое исключение для TodoJournal."""
    pass


class TodoJournal:
    """Класс для управления todo-журналом."""

    def __init__(self, path_todo: str):
        self.path_todo = path_todo
        data = self._parse()
        self.name: str = data["name"]
        self.entries: List[str] = data["todos"]

    def _parse(self) -> Dict[str, Union[str, List[str]]]:
        """Чтение и парсинг JSON-файла."""
        try:
            with open(self.path_todo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            sys.exit(1)

    def _update(self, new_data: Dict[str, Union[str, List[str]]]) -> None:
        """Запись данных в файл."""
        with open(self.path_todo, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, sort_keys=True, indent=4, ensure_ascii=False)

    @staticmethod
    def create(filename: str, name: str) -> None:
        """Создание нового пустого журнала."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({'name': name, 'todos': []}, f, sort_keys=True, indent=4, ensure_ascii=False)

    def add_entry(self, new_entry: str) -> None:
        """Добавление задачи."""
        self.entries.append(new_entry)
        self._update({'name': self.name, 'todos': self.entries})

    def remove_entry(self, index: int) -> None:
        """Удаление задачи по индексу."""
        del self.entries[index]
        self._update({'name': self.name, 'todos': self.entries})