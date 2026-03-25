#Модуль для работы с журналом
import json
import sys
from typing import Dict, List, Union, NoReturn


# Базовое исключение для журнала (мб пригодится)
class TodoJournalError(Exception):
    pass

#==============Класс для управления журналом===================
class TodoJournal:

    def __init__(self, path_todo: str):
        self.path_todo = path_todo
        data = self._parse()
        self.name: str = data["name"]
        self.entries: List[str] = data["todos"]

    # Чтение и парсинг JSON
    def _parse(self) -> Dict[str, Union[str, List[str]]]:
        try:
            with open(self.path_todo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            sys.exit(1)

    # Запись данных в файл
    def _update(self, new_data: Dict[str, Union[str, List[str]]]) -> None:
        with open(self.path_todo, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, sort_keys=True, indent=4, ensure_ascii=False)

    #Создание нового пустого журнала (единоразовый метод)
    @staticmethod
    def create(filename: str, name: str) -> None:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({'name': name, 'todos': []}, f, sort_keys=True, indent=4, ensure_ascii=False)

    # Добавление задачи
    def add_entry(self, new_entry: str) -> None:
        self.entries.append(new_entry)
        self._update({'name': self.name, 'todos': self.entries})

    #Удаление задачи по индексу
    def remove_entry(self, index: int) -> None:
        del self.entries[index]
        self._update({'name': self.name, 'todos': self.entries})