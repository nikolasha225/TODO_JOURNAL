import tkinter as tk
from tkinter import ttk, messagebox

from src.config import save_config
from src.logger import get_logger
import os

logger = get_logger()

class AddEditDialog(tk.Toplevel):
    def __init__(self, parent, title="Введите задачу", initial_text=""):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.geometry("500x300")

        # Текстовое поле (многострочное)
        label = ttk.Label(self, text="Текст задачи:")
        label.pack(pady=5)
        self.text = tk.Text(self, wrap=tk.WORD, height=10, width=60)
        self.text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.text.insert("1.0", initial_text)
        self.text.focus_set()

        # Добавляем прокрутку
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar.set)

        # Кнопки
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.on_cancel).pack(side=tk.LEFT, padx=5)

        self.text.bind("<Control-Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())

    def on_ok(self):
        self.result = self.text.get("1.0", tk.END).strip()
        logger.debug(f"on_ok: result={self.result}")
        if not self.result:
            messagebox.showwarning("Предупреждение", "Задача не может быть пустой")
            return
        self.destroy()

    def on_cancel(self):
        logger.debug("on_cancel called")
        self.result = None
        self.destroy()

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, config, config_path):
        super().__init__(parent)
        self.config = config
        self.config_path = config_path
        self.title("Настройки")
        self.geometry("450x200")

        # Editor selection
        ttk.Label(self, text="Редактор по умолчанию:").pack(pady=5)
        editor_frame = ttk.Frame(self)
        editor_frame.pack(fill=tk.X, padx=10)
        self.editor_var = tk.StringVar(value=config.get("editor", ""))
        self.editor_entry = ttk.Entry(editor_frame, textvariable=self.editor_var, width=40)
        self.editor_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(editor_frame, text="Обзор...", command=self.browse_editor).pack(side=tk.LEFT)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def browse_editor(self):
        # Open file picker for executable
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Выберите редактор",
            filetypes=[("Исполняемые файлы", "*.exe"), ("Все файлы", "*.*")] if os.name == 'nt' else [("Все файлы", "*.*")]
        )
        if file_path:
            self.editor_var.set(file_path)

    def save(self):
        new_editor = self.editor_var.get().strip()
        self.config["editor"] = new_editor if new_editor else None
        try:
            from src.config import save_config
            save_config(self.config, self.config_path)
            logger.info(f"Сохранён редактор: {new_editor}")
            messagebox.showinfo("Успешно", "Настройки сохранены")
            self.destroy()
        except Exception as e:
            logger.exception("Ошибка сохранения конфига")
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки:\n{e}")

    def cancel(self):
        self.result = None
        self.destroy()