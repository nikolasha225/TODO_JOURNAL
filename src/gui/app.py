import sys
import os
from tkinter import Tk, messagebox, simpledialog, filedialog
from src.config import load_config, get_config_path, save_config
from src.logger import setup_logging, get_logger
from src.exceptions import TodoJournalError
from src.todo_journal import TodoJournal
from src.gui.main_window import MainWindow, logger
import src.logger

#Основная функция программы
def main():
    setup_logging("logging.ini")
    logger = get_logger()
    logger.info("Запуск приложения")

    # Загружаем конфигурацию
    try:
        config_path = get_config_path()
        config_data = load_config(config_path)
    except TodoJournalError as e:
        logger.error(f"Ошибка загрузки конфигурации: {e.message}")
        print(e.message)
        sys.exit(1)

    journal_path = config_data.get("current_journal")
    if not journal_path or not os.path.exists(journal_path):
        logger.info("Текущий журнал не задан или не существует, предлагаем выбрать/создать")
        journal_path = select_or_create_journal()
        if not journal_path:
            logger.warning("Пользователь не выбрал журнал, выход")
            return
        # Сохраняем выбранный путь в конфиг
        config_data["current_journal"] = journal_path
        try:
            save_config(config_data, config_path)
            logger.info(f"Путь к журналу сохранён в конфиг: {journal_path}")
        except Exception as e:
            logger.exception("Ошибка сохранения конфига")
            messagebox.showerror("Ошибка", f"Не удалось сохранить путь в конфигурацию:\n{e}")

    # Создаём объект TodoJournal
    try:
        journal = TodoJournal(journal_path)
    except TodoJournalError as e:
        logger.error(f"Ошибка открытия журнала: {e.message}")
        messagebox.showerror("Ошибка", e.message)
        sys.exit(1)

    # Запуск GUI
    app = MainWindow(journal)
    app.mainloop()

    logger.info("Приложение завершено")

#Выбрать или создать журнал
def select_or_create_journal():
    root = Tk()
    root.withdraw()  # Скрыть главное окно

    choice = messagebox.askyesno("Выбор журнала", "Создать новый журнал?\nНажмите 'Да' для создания, 'Нет' для открытия существующего.")
    if choice:
        # Создание нового журнала
        name = simpledialog.askstring("Название журнала", "Введите название журнала:")
        if not name:
            return None
        # Предложить сохранить файл
        default_filename = f"todo_{name}.json"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Сохранить журнал как"
        )
        if not file_path:
            return None
        try:
            TodoJournal.create(file_path, name)
            return file_path
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать журнал:\n{e}")
            return None
    else:
        # Открыть существующий журнал
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Выберите файл журнала"
        )
        if not file_path:
            return None
        return file_path

if __name__ == "__main__":
    main()