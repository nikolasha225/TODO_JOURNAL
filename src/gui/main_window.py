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

    #Обновить отображение списка задач
    def refresh_list(self):
        logger.debug(f"Обновление списка, записей: {len(self.journal.entries)}")
        self.listbox.delete(0, tk.END)
        for i, task in enumerate(self.journal.entries, start=1):
            self.listbox.insert(tk.END, f"{i}. {task}")
        self.status.config(text=f"Всего задач: {len(self.journal.entries)}")

    def add_task(self):
        logger.debug("Вызвана add_task")
        dialog = AddEditDialog(self, title="Добавить задачу")
        self.wait_window(dialog)  # Ждём, пока диалог не закроется
        logger.debug(f"after dialog, result={dialog.result}")
        if dialog.result:
            try:
                logger.info(f"Попытка добавить задачу: {dialog.result}")
                self.journal.add_entry(dialog.result)
                logger.info(f"Задача добавлена: {dialog.result}")
                self.refresh_list()
            except Exception as e:
                logger.exception("Ошибка при добавлении")
                messagebox.showerror("Ошибка", f"Не удалось добавить задачу:\n{e}")

    def edit_task(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите задачу для редактирования")
            return
        idx = selection[0]
        old_text = self.journal.entries[idx]
        dialog = AddEditDialog(self, title="Редактировать задачу", initial_text=old_text)
        if dialog.result and dialog.result != old_text:
            try:
                self.journal.edit_entry(idx, dialog.result)
                logger.info(f"Изменена задача {idx+1}: {old_text} -> {dialog.result}")
                self.refresh_list()
            except Exception as e:
                logger.exception("Ошибка при редактировании")
                messagebox.showerror("Ошибка", f"Не удалось изменить задачу:\n{e}")

    def delete_task(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите задачу для удаления")
            return
        idx = selection[0]
        task_text = self.journal.entries[idx]
        if messagebox.askyesno("Подтверждение", f"Удалить задачу:\n{task_text}?"):
            try:
                self.journal.remove_entry(idx)
                logger.info(f"Удалена задача {idx+1}: {task_text}")
                self.refresh_list()
            except Exception as e:
                logger.exception("Ошибка при удалении")
                messagebox.showerror("Ошибка", f"Не удалось удалить задачу:\n{e}")

    def open_settings(self):
        #TODO: окно настроек
        messagebox.showinfo("Информация", "Настройки пока не реализованы")