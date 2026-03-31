import json
from typing import Dict, List, Union, Any, Optional, Iterator
from src.exceptions import TodoJournalError
from src.logger import get_logger

logger = get_logger()

class TodoJournal:
    _readonly_attrs = {'first', 'last'}

    def __init__(self, path_todo: str):
        self.path_todo = path_todo
        data = self._parse()
        if "name" not in data or "todos" not in data:
            raise TodoJournalError("TodoJournalFormatError",
                                   journal_name=data.get("name", "unknown"),
                                   journal_path=path_todo)
        self.name: str = data["name"]
        # Преобразуем старый формат (строка) в новый (словарь)
        raw_entries = data["todos"]
        self.entries: List[Dict[str, Any]] = []
        for e in raw_entries:
            if isinstance(e, str):
                self.entries.append({"text": e, "due_date": None})
            elif isinstance(e, dict):
                # Убедимся, что есть ключи
                self.entries.append({"text": e.get("text", ""), "due_date": e.get("due_date")})
            else:
                self.entries.append({"text": str(e), "due_date": None})

    #Чтение и парсинг JSON-файла
    def _parse(self) -> Dict[str, Union[str, List[Any]]]:
        try:
            with open(self.path_todo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise TodoJournalError("TodoJournalFormatError",
                journal_name="unknown",
                journal_path=self.path_todo) from e

    def _update(self, new_data: Dict[str, Any]) -> None:
        """Запись данных в файл."""
        try:
            with open(self.path_todo, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, sort_keys=True, indent=4, ensure_ascii=False)
        except OSError as e:
            raise TodoJournalError("TodoJournalFormatError",
                                   journal_name=self.name,
                                   journal_path=self.path_todo) from e

    @staticmethod
    def create(filename: str, name: str) -> None:
        """Создание нового пустого журнала."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({'name': name, 'todos': []}, f, sort_keys=True, indent=4, ensure_ascii=False)

    def add_entry(self, new_text: str, due_date: Optional[str] = None) -> None:
        """Добавляет задачу с текстом и опциональной датой."""
        self.entries.append({"text": new_text, "due_date": due_date})
        self._update({'name': self.name, 'todos': self.entries})

    def edit_entry(self, index: int, new_text: Optional[str] = None, new_due_date: Optional[str] = None) -> None:
        """Редактирует задачу по индексу. Если new_text или new_due_date не переданы, оставляет старые значения."""
        if 0 <= index < len(self.entries):
            if new_text is not None:
                self.entries[index]["text"] = new_text
            if new_due_date is not None:
                self.entries[index]["due_date"] = new_due_date
            self._update({'name': self.name, 'todos': self.entries})
        else:
            raise IndexError(f"Индекс {index} вне диапазона")

    def remove_entry(self, index: int) -> None:
        """Удаляет задачу по индексу."""
        del self.entries[index]
        self._update({'name': self.name, 'todos': self.entries})

    def get_task_text(self, index: int) -> str:
        return self.entries[index]["text"]

    def get_task_due(self, index: int) -> Optional[str]:
        return self.entries[index]["due_date"]

    # === Магические методы ===
    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self) -> Iterator[str]:
        for e in self.entries:
            yield e["text"]

    def __getitem__(self, index: Any) -> Any:
        if isinstance(index, int):
            return self.entries[index]["text"]
        else:
            # срезы возвращают список текстов
            return [e["text"] for e in self.entries[index]]

    def __getattr__(self, name: str) -> Any:
        if name == 'first':
            if self.entries:
                return self.entries[0]["text"]
            raise AttributeError("Нет задач в журнале")
        if name == 'last':
            if self.entries:
                return self.entries[-1]["text"]
            raise AttributeError("Нет задач в журнале")
        raise AttributeError(f"{type(self).__name__} не имеет атрибута '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._readonly_attrs:
            raise AttributeError(f"Атрибут '{name}' доступен только для чтения")
        super().__setattr__(name, value)