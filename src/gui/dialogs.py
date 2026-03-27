import tkinter as tk
from tkinter import ttk, messagebox

class AddEditDialog(tk.Toplevel):
    def __init__(self, parent, title="Введите задачу", initial_text=""):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.geometry("400x150")

        # Текстовое поле
        label = ttk.Label(self, text="Текст задачи:")
        label.pack(pady=5)
        self.entry = ttk.Entry(self, width=50)
        self.entry.insert(0, initial_text)
        self.entry.pack(pady=5)
        self.entry.focus_set()
        self.entry.select_range(0, tk.END)

        # Кнопки
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.on_cancel).pack(side=tk.LEFT, padx=5)

        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())

    def on_ok(self):
        self.result = self.entry.get().strip()
        if not self.result:
            messagebox.showwarning("Предупреждение", "Задача не может быть пустой")
            return
        self.destroy()

    def on_cancel(self):
        self.destroy()


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.title("Настройки")
        self.geometry("400x200")

        # Поле для редактора
        ttk.Label(self, text="Редактор по умолчанию:").pack(pady=5)
        self.editor_entry = ttk.Entry(self, width=40)
        self.editor_entry.insert(0, config.get("editor", ""))
        self.editor_entry.pack(pady=5)

        # Путь к журналу (пока не реализовано управление несколькими)
        ttk.Label(self, text="Текущий журнал:").pack(pady=5)
        self.journal_path_label = ttk.Label(self, text=config.get("current_journal", "Не задан"))
        self.journal_path_label.pack(pady=5)

        # Кнопки
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def save(self):
        self.config["editor"] = self.editor_entry.get().strip()
        #TODO: сохранить через config.save_config
        self.destroy()