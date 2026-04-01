#Тесты для класса TodoJournal


import json
import pytest
from src.todo_journal import TodoJournal


#Фикстура: журнал с тремя задачами
@pytest.fixture
def journal_with_entries(tmpdir):
    todo_path = tmpdir.join("test.todo")
    TodoJournal.create(todo_path, "test")
    journal = TodoJournal(todo_path)
    journal.add_entry("Задача 1")
    journal.add_entry("Задача 2")
    journal.add_entry("Задача 3")
    return journal


#Проверка создания журнала
def test_create(tmpdir):
    todo_path = tmpdir.join("test.todo")
    expected_name = "test_journal"
    TodoJournal.create(todo_path, expected_name)

    with open(todo_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert data["name"] == expected_name
    assert data["todos"] == []


#Проверка добавления задачи
def test_add_entry(tmpdir):
    todo_path = tmpdir.join("test.todo")
    TodoJournal.create(todo_path, "test")
    journal = TodoJournal(todo_path)
    journal.add_entry("Помыть посуду")
    assert journal.entries == [{"text": "Помыть посуду", "due_date": None}]


#Проверка удаления задачи
def test_remove_entry(tmpdir):
    todo_path = tmpdir.join("test.todo")
    TodoJournal.create(todo_path, "test")
    journal = TodoJournal(todo_path)
    journal.add_entry("Задача 1")
    journal.add_entry("Задача 2")
    journal.remove_entry(0)
    assert journal.entries == [{"text": "Задача 2", "due_date": None}]


#Проверка __len__
def test_len(journal_with_entries):
    assert len(journal_with_entries) == 3


#Проверка __iter__
def test_iter(journal_with_entries):
    tasks = list(journal_with_entries)
    assert tasks == ["Задача 1", "Задача 2", "Задача 3"]


#Проверка __getitem__
def test_getitem(journal_with_entries):
    assert journal_with_entries[0] == "Задача 1"
    assert journal_with_entries[1] == "Задача 2"
    assert journal_with_entries[2] == "Задача 3"
    assert journal_with_entries[-1] == "Задача 3"
    #Срезы
    assert journal_with_entries[1:3] == ["Задача 2", "Задача 3"]


#Проверка __getattr__ для first и last
def test_getattr_first_last(journal_with_entries):
    assert journal_with_entries.first == "Задача 1"
    assert journal_with_entries.last == "Задача 3"


#Проверка __getattr__ для пустого
def test_getattr_empty_journal(tmpdir):
    todo_path = tmpdir.join("empty.todo")
    TodoJournal.create(todo_path, "empty")
    journal = TodoJournal(todo_path)

    with pytest.raises(AttributeError, match="Нет задач в журнале"):
        _ = journal.first
    with pytest.raises(AttributeError, match="Нет задач в журнале"):
        _ = journal.last


#Проверка __setattr__ – нельзя изменить first и last
def test_setattr_readonly(journal_with_entries):
    with pytest.raises(AttributeError, match="Атрибут 'first' доступен только для чтения"):
        journal_with_entries.first = "Новая задача"
    with pytest.raises(AttributeError, match="Атрибут 'last' доступен только для чтения"):
        journal_with_entries.last = "Новая задача"

    #Но можно установить другие атрибуты
    journal_with_entries.new_attr = "работает"
    assert journal_with_entries.new_attr == "работает"


#Проверка edit_entry
def test_edit_entry(journal_with_entries, tmpdir):
    journal_with_entries.edit_entry(1, "Изменённая задача")
    assert journal_with_entries.entries == [
        {"text": "Задача 1", "due_date": None},
        {"text": "Изменённая задача", "due_date": None},
        {"text": "Задача 3", "due_date": None}
    ]
    #Проверка выхода за границы
    with pytest.raises(IndexError):
        journal_with_entries.edit_entry(10, "несуществующая")

def test_add_entry_with_date(tmpdir):
    todo_path = tmpdir.join("test.todo")
    TodoJournal.create(todo_path, "test")
    journal = TodoJournal(todo_path)
    journal.add_entry("Задача с датой", "2025-12-31")
    assert journal.entries == [{"text": "Задача с датой", "due_date": "2025-12-31"}]

def test_edit_entry_with_date(journal_with_entries):
    journal_with_entries.edit_entry(1, new_due_date="2025-12-31")
    assert journal_with_entries.entries[1]["due_date"] == "2025-12-31"