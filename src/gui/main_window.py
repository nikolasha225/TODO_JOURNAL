import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
from src.todo_journal import TodoJournal
from src.logger import get_logger
from src.gui.dialogs import AddEditDialog, SettingsDialog

logger = get_logger()

class MainWindow(tk.Tk):
    def __init__(self, journal: TodoJournal):
        super().__init__()
        self.journal = journal
        self.title(f"Todo Journal: {journal.name}")
        self.geometry("500x400")

        # Список задач
        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE, activestyle='none')
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопки
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Добавить", command=self.add_task).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Редактировать", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_task).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Обновить", command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Настройки", command=self.open_settings).pack(side=tk.LEFT, padx=5)

        # Статусная строка
        self.status = tk.Label(self, text="Готов", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.refresh_list()

