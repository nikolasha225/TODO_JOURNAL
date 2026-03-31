import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from src.logger import get_logger

logger = get_logger()

class AddEditDialog(tk.Toplevel):
    def __init__(self, parent, title="Введите задачу", initial_text="", initial_due=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.geometry("500x400")

        # Текст задачи
        ttk.Label(self, text="Текст задачи:").pack(pady=5)
        self.text = tk.Text(self, wrap=tk.WORD, height=8, width=60)
        self.text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.text.insert("1.0", initial_text)
        self.text.focus_set()

        # Прокрутка для текста
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar.set)

        # Рамка для даты
        date_frame = ttk.Frame(self)
        date_frame.pack(fill=tk.X, padx=10, pady=5)

        # Чекбокс для включения даты
        self.use_date = tk.BooleanVar(value=True)
        date_check = ttk.Checkbutton(date_frame, text="Установить дату", variable=self.use_date,
                                     command=self.toggle_date_entry)
        date_check.pack(side=tk.LEFT, padx=5)

        # Поле ввода даты
        self.due_entry = ttk.Entry(date_frame, width=12)
        self.due_entry.pack(side=tk.LEFT, padx=5)

        # Если при редактировании есть дата, заполняем поле и включаем чекбокс
        if initial_due:
            self.due_entry.insert(0, initial_due)
            self.use_date.set(True)
        else:
            # По умолчанию ставим текущую дату, если чекбокс включён
            self.due_entry.insert(0, date.today().isoformat())
            self.use_date.set(True)

        self.toggle_date_entry()  # установить начальное состояние

        # Кнопки
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.on_cancel).pack(side=tk.LEFT, padx=5)

        self.bind("<Control-Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())

    #Включает/выключает поле ввода даты
    def toggle_date_entry(self):
        if self.use_date.get():
            self.due_entry.config(state="normal")
        else:
            self.due_entry.config(state="disabled")

    def on_ok(self):
        text = self.text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Задача не может быть пустой")
            return

        due = None
        if self.use_date.get():
            due_val = self.due_entry.get().strip()
            if due_val:
                due = due_val

        self.result = {"text": text, "due_date": due}
        self.destroy()

    def on_cancel(self):
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