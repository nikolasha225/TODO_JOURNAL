import sys

from config import save_config
from src.config import load_config, get_config_path
from src.logger import setup_logging, get_logger
from src.exceptions import TodoJournalError
from src.todo_journal import TodoJournal
from src.gui.main_window import MainWindow

#Основная функция программы
def main():
    # Настройка логирования
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

    # Получаем путь к текущему журналу
    journal_path = config_data.get("current_journal")
    if not journal_path:
        logger.warning("Текущий журнал не указан в конфигурации")
        journal_path = select_or_create_journal()
        if journal_path:
            # обновляем конфиг
            config_data["current_journal"] = journal_path
            save_config(config_data)
        else:
            logger.info("Пользователь отменил выбор журнала, выход")
            return

    # Создаём объект TodoJournal
    try:
        journal = TodoJournal(journal_path)
    except TodoJournalError as e:
        logger.error(f"Ошибка открытия журнала: {e.message}")
        print(e.message)
        sys.exit(1)

    #Запуск GUI
    app = MainWindow(journal)
    app.mainloop()

    print("Запуск GUI пока не реализован")
    logger.info("Приложение завершено")

#Выбрать или создать журнал
def select_or_create_journal():
    from tkinter import Tk, filedialog, messagebox
    root = Tk()
    root.withdraw()  # скрыть главное окно
    choice = messagebox.askyesno("Журнал не найден",
                                  "У вас нет текущего журнала. Хотите выбрать существующий? (Да - выбрать, Нет - создать новый)")
    if choice:
        # Выбрать существующий
        file_path = filedialog.askopenfilename(
            title="Выберите файл журнала",
            filetypes=[("JSON files", "*.json"), ("Todo files", "*.todo"), ("All files", "*.*")]
        )
        if file_path:
            return file_path
        else:
            # пользователь отменил
            return None
    else:
        # Создать новый
        file_path = filedialog.asksaveasfilename(
            title="Создать новый журнал",
            defaultextension=".todo",
            filetypes=[("Todo files", "*.todo"), ("JSON files", "*.json")]
        )
        if file_path:
            name = filedialog.askstring("Название журнала", "Введите название журнала:")
            if name:
                TodoJournal.create(file_path, name)
                return file_path
            else:
                return None
        else:
            return None

if __name__ == "__main__":
    main()