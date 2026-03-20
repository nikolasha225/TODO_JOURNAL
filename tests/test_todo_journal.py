"""Тесты для класса TodoJournal."""
import json
import pytest
from src.todo_journal import TodoJournal


def test_create(tmpdir):
    """Проверка создания журнала."""
    todo_path = tmpdir.join("test.todo")
    expected_name = "test_journal"
    TodoJournal.create(todo_path, expected_name)

    with open(todo_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert data["name"] == expected_name
    assert data["todos"] == []


def test_add_entry(tmpdir):
    """Проверка добавления задачи."""
    todo_path = tmpdir.join("test.todo")
    TodoJournal.create(todo_path, "test")
    journal = TodoJournal(todo_path)

    journal.add_entry("Помыть посуду")
    assert journal.entries == ["Помыть посуду"]

    with open(todo_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data["todos"] == ["Помыть посуду"]


def test_remove_entry(tmpdir):
    """Проверка удаления задачи."""
    todo_path = tmpdir.join("test.todo")
    TodoJournal.create(todo_path, "test")
    journal = TodoJournal(todo_path)
    journal.add_entry("Задача 1")
    journal.add_entry("Задача 2")

    journal.remove_entry(0)
    assert journal.entries == ["Задача 2"]

    with open(todo_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data["todos"] == ["Задача 2"]