import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from src.config import add_journal, remove_journal, set_current_journal, get_journal_path
from src.todo_journal import TodoJournal
from src.logger import get_logger
from src.gui.dialogs import AddEditDialog, SettingsDialog

logger = get_logger()

#Главное окно проги
class MainWindow(tk.Tk):
    def __init__(self, journal: TodoJournal, config: dict, config_path: str):
        super().__init__()
        self.journal = journal
        self.config = config
        self.config_path = config_path
        self.title(f"Todo Journal: {journal.name}")
        self.geometry("600x500")

        #Верхняя панель - выбор журнала
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.top_frame, text="Журнал:").pack(side=tk.LEFT, padx=5)
        self.journal_var = tk.StringVar()
        self.journal_combo = ttk.Combobox(self.top_frame, textvariable=self.journal_var,
                                          state="readonly", width=30)
        self.journal_combo.pack(side=tk.LEFT, padx=5)
        self.journal_combo.bind("<<ComboboxSelected>>", self.on_journal_change)

        ttk.Button(self.top_frame, text="Создать", command=self.create_journal).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.top_frame, text="Удалить", command=self.delete_journal).pack(side=tk.LEFT, padx=2)

        #Список задач
        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE, activestyle='none')
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        #Кнопки действий
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Добавить", command=self.add_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Настройки", command=self.open_settings).pack(side=tk.LEFT, padx=5)

        #Статусная строка
        self.status = tk.Label(self, text="Готов", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        #Заполняем комбобокс
        self.refresh_journal_list()
        self.refresh_list()

    #---------Журналы-----------
    #обновляет список журналов в комбобоксе
    def refresh_journal_list(self):
        names = list(self.config["journals"].keys())
        self.journal_combo['values'] = names
        current = self.config.get("current_journal")
        if current in names:
            self.journal_var.set(current)
        else:
            self.journal_var.set("")

    #Обработчик выбора журнала
    def on_journal_change(self, event):
        logger.debug("Выбираем журнал")
        new_name = self.journal_var.get()
        if not new_name:
            return
        path = self.config["journals"].get(new_name)
        if not path:
            messagebox.showerror("Ошибка", f"Путь к журналу '{new_name}' не найден")
            return
        try:
            new_journal = TodoJournal(path)
            self.journal = new_journal
            self.config = set_current_journal(self.config, new_name)
            from src.config import save_config
            save_config(self.config, self.config_path)
            self.title(f"Todo Journal: {new_journal.name}")
            self.refresh_list()
        except Exception as e:
            logger.exception("Ошибка при переключении журнала")
            messagebox.showerror("Ошибка", f"Не удалось открыть журнал:\n{e}")

    #Создать новый журнал
    def create_journal(self):
        logger.debug("Создаём новый журнал")
        name = simpledialog.askstring("Новый журнал", "Введите название журнала:")
        if not name:
            return
        # Предложить сохранить файл
        from tkinter import filedialog
        default_filename = f"todo_{name}.json"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Сохранить журнал как"
        )
        if not file_path:
            return
        try:
            TodoJournal.create(file_path, name)
            # Добавляем в конфиг
            self.config = add_journal(self.config, name, file_path)
            self.config = set_current_journal(self.config, name)
            from src.config import save_config
            save_config(self.config, self.config_path)
            # Переключаемся на новый журнал
            self.journal = TodoJournal(file_path)
            self.refresh_journal_list()
            self.refresh_list()
            logger.info(f"Создан журнал '{name}' в {file_path}")
        except Exception as e:
            logger.exception("Ошибка создания журнала")
            messagebox.showerror("Ошибка", f"Не удалось создать журнал:\n{e}")

    #Удалить выбранный журнал (удаление только из конфига)
    def delete_journal(self):
        name = self.journal_var.get()
        if not name:
            messagebox.showinfo("Информация", "Нет выбранного журнала")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить журнал '{name}' из списка?\nФайл останется на диске."):
            self.config = remove_journal(self.config, name)
            from src.config import save_config
            save_config(self.config, self.config_path)
            # Если удалили текущий, нужно выбрать другой или создать новый
            if not self.config.get("current_journal"):
                # Можно попробовать выбрать первый доступный
                first = next(iter(self.config["journals"].keys()), None)
                if first:
                    self.config = set_current_journal(self.config, first)
                    path = self.config["journals"][first]
                    self.journal = TodoJournal(path)
                else:
                    # Нет журналов – создаём новый?
                    self.create_journal()
                    return
            else:
                # Текущий не удалялся, но нужно перезагрузить журнал
                path = self.config["journals"][self.config["current_journal"]]
                self.journal = TodoJournal(path)
            self.refresh_journal_list()
            self.refresh_list()

    #-------------тудушки----------------
    #Добавить задачу
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

    #Обновить отображение списка задач
    def refresh_list(self):
        logger.debug(f"Обновление списка, записей: {len(self.journal.entries)}")
        self.listbox.delete(0, tk.END)
        for i, task in enumerate(self.journal.entries, start=1):
            self.listbox.insert(tk.END, f"{i}. {task}")
        self.status.config(text=f"Всего задач: {len(self.journal.entries)}")

    def edit_task(self):
        logger.debug("edit_task called")
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите задачу для редактирования")
            return
        idx = selection[0]
        old_text = self.journal.entries[idx]
        dialog = AddEditDialog(self, title="Редактировать задачу", initial_text=old_text)
        self.wait_window(dialog)
        logger.debug(f"after dialog, result={dialog.result}")
        if dialog.result and dialog.result != old_text:
            try:
                logger.info(f"Попытка изменить задачу {idx + 1}: {old_text} -> {dialog.result}")
                self.journal.edit_entry(idx, dialog.result)
                logger.info(f"Задача изменена")
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