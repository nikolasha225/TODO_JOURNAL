#Модуль для работы с журналом


import json
import sys
from typing import Dict, List, Union, NoReturn, Iterator, Any
from src.logger import get_logger

logger = get_logger()

#==============Класс для управления журналом===================
class TodoJournal:

    #Константные динамические атрибуты
    _readonly_attrs = {'first', 'last'}

    #Конструктор
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
    def _update(self, new_data: dict) -> None:
        logger.debug(f"Запись в файл {self.path_todo}: {new_data}")
        with open(self.path_todo, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, sort_keys=True, indent=4, ensure_ascii=False)
        logger.debug("Запись завершена")

    #Создание нового пустого журнала (единоразовый метод)
    @staticmethod
    def create(filename: str, name: str) -> None:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({'name': name, 'todos': []}, f, sort_keys=True, indent=4, ensure_ascii=False)

    # Добавление задачи
    def add_entry(self, new_entry: str) -> None:
        logger.debug(f"add_entry: {new_entry}, текущий список: {self.entries}")
        self.entries.append(new_entry)
        logger.debug(f"Новый список: {self.entries}")
        self._update({'name': self.name, 'todos': self.entries})

    #Удаление задачи по индексу
    def remove_entry(self, index: int) -> None:
        del self.entries[index]
        self._update({'name': self.name, 'todos': self.entries})

    #Редактирование задачи по индексу
    def edit_entry(self, index: int, new_text: str) -> None:
        logger.debug(f"edit_entry called: index={index}, new_text={new_text}")
        if 0 <= index < len(self.entries):
            self.entries[index] = new_text
            self._update({'name': self.name, 'todos': self.entries})
            logger.debug("edit_entry updated")
        else:
            raise IndexError(f"Индекс {index} вне диапазона")

    #--------magic метрды------------

    #Возвращает количество задач
    def __len__(self) -> int:
        return len(self.entries)

    #Итератор по задачам
    def __iter__(self) -> Iterator[str]:
        return iter(self.entries)

    #Человеческий индекс (поддерживает срезы)
    def __getitem__(self, index: Any) -> Any:
        return self.entries[index]

    #Динамический доступ к first и last (по другим нельзя вызвать)
    def __getattr__(self, name: str) -> Any:
        if name == 'first':
            if self.entries:
                return self.entries[0]
            raise AttributeError("Нет задач в журнале")
        if name == 'last':
            if self.entries:
                return self.entries[-1]
            raise AttributeError("Нет задач в журнале")
        raise AttributeError(f"{type(self).__name__} не имеет атрибута '{name}'")

    #Защита атрибутов first и last от изменения
    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._readonly_attrs:
            raise AttributeError(f"Атрибут '{name}' доступен только для чтения")
        super().__setattr__(name, value)