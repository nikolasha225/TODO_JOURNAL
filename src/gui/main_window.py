import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from src.config import add_journal, remove_journal, set_current_journal, get_journal_path
from src.todo_journal import TodoJournal
from src.logger import get_logger
from src.gui.dialogs import AddEditDialog, SettingsDialog
import json
import tempfile
import subprocess
import os
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
        ttk.Button(self.top_frame, text="Открыть", command=self.open_existing_journal).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.top_frame, text="Удалить", command=self.delete_journal).pack(side=tk.LEFT, padx=2)

        #Список задач
        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE, activestyle='none')
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        #Кнопки действий
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Добавить", command=self.add_task).pack(side=tk.LEFT, padx=5)

        # Кнопка с выпадающим меню для редактирования
        self.edit_menubutton = ttk.Menubutton(button_frame, text="Редактировать")
        self.edit_menu = tk.Menu(self.edit_menubutton, tearoff=0)
        self.edit_menu.add_command(label="Встроенный редактор", command=self.edit_task_internal)
        self.edit_menu.add_command(label="Внешний редактор", command=self.edit_task_external)
        self.edit_menubutton.configure(menu=self.edit_menu)
        self.edit_menubutton.pack(side=tk.LEFT, padx=5)

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

    #Открыть существующий файл журнала и добавить его в конфиг
    def open_existing_journal(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Выберите файл журнала"
        )
        if not file_path:
            return
        try:
            # Проверяем, можно ли прочитать как журнал
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "name" not in data or "todos" not in data:
                messagebox.showerror("Ошибка", "Файл не является корректным журналом Todo.")
                return
            name = data["name"]
            # Если имя уже существует в конфиге, предложим другое
            if name in self.config["journals"]:
                name = simpledialog.askstring("Имя журнала",
                                              f"Журнал с именем '{name}' уже существует. Введите другое имя:",
                                              initialvalue=name + "_new")
                if not name:
                    return
            # Добавляем в конфиг
            self.config = add_journal(self.config, name, file_path)
            self.config = set_current_journal(self.config, name)
            from src.config import save_config
            save_config(self.config, self.config_path)
            # Загружаем журнал
            self.journal = TodoJournal(file_path)
            self.refresh_journal_list()
            self.refresh_list()
            logger.info(f"Открыт существующий журнал '{name}' из {file_path}")
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл не является корректным JSON.")
        except Exception as e:
            logger.exception("Ошибка при открытии журнала")
            messagebox.showerror("Ошибка", f"Не удалось открыть журнал:\n{e}")

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
            # Показываем первую строку задачи
            first_line = task.split('\n')[0]
            self.listbox.insert(tk.END, f"{i}. {first_line}")
        self.status.config(text=f"Всего задач: {len(self.journal.entries)}")

    #Обычный эдит таск
    def edit_task_internal(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите задачу для редактирования")
            return
        idx = selection[0]
        old_text = self.journal.entries[idx]
        dialog = AddEditDialog(self, title="Редактировать задачу", initial_text=old_text)
        self.wait_window(dialog)
        if dialog.result and dialog.result != old_text:
            try:
                logger.info(f"Попытка изменить задачу {idx + 1}: {old_text} -> {dialog.result}")
                self.journal.edit_entry(idx, dialog.result)
                logger.info(f"Задача изменена")
                self.refresh_list()
            except Exception as e:
                logger.exception("Ошибка при редактировании")
                messagebox.showerror("Ошибка", f"Не удалось изменить задачу:\n{e}")

    #Редактирование задачи во внешнем редакторе
    def edit_task_external(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите задачу для редактирования")
            return
        idx = selection[0]
        task_text = self.journal.entries[idx]

        # Получаем редактор из конфига
        editor = self.config.get("editor")
        if not editor:
            messagebox.showerror("Ошибка", "Редактор не задан в настройках.\nЗадайте его в файле конфигурации.")
            return

        # Создаём временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(task_text)
            temp_path = f.name

        try:
            # Запускаем редактор
            subprocess.run([editor, temp_path], check=True)
            # Читаем изменённый текст
            with open(temp_path, 'r', encoding='utf-8') as f:
                new_text = f.read().strip()
            if new_text and new_text != task_text:
                self.journal.edit_entry(idx, new_text)
                logger.info(f"Задача {idx + 1} изменена внешним редактором: {task_text} -> {new_text}")
                self.refresh_list()
            elif not new_text:
                messagebox.showwarning("Предупреждение", "Задача не может быть пустой. Изменения отменены.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка запуска редактора: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть редактор:\n{e}")
        except Exception as e:
            logger.exception("Ошибка при внешнем редактировании")
            messagebox.showerror("Ошибка", f"Не удалось отредактировать задачу:\n{e}")
        finally:
            # Удаляем временный файл
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def delete_task(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите задачу для удаления")
            return
        idx = selection[0]
        full_text = self.journal.entries[idx]
        first_line = full_text.split('\n')[0]
        if messagebox.askyesno("Подтверждение", f"Удалить задачу:\n{first_line}?"):
            try:
                self.journal.remove_entry(idx)
                logger.info(f"Удалена задача {idx + 1}: {first_line}")
                self.refresh_list()
            except Exception as e:
                logger.exception("Ошибка при удалении")
                messagebox.showerror("Ошибка", f"Не удалось удалить задачу:\n{e}")

    def open_settings(self):
        from src.gui.dialogs import SettingsDialog
        SettingsDialog(self, self.config, self.config_path).wait_window()
        logger.debug("Настройки обновлены")