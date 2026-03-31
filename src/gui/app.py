import sys
import os
from tkinter import Tk, messagebox, simpledialog, filedialog
from src.config import load_config, get_config_path, save_config, add_journal, set_current_journal
from src.logger import setup_logging, get_logger
from src.exceptions import TodoJournalError
from src.todo_journal import TodoJournal
from src.gui.main_window import MainWindow, logger
import src.logger

#Основная функция программы
def main():
    setup_logging("logging.ini")
    logger.info("Запуск приложения")

    # Загружаем конфигурацию
    try:
        config_path = get_config_path()
        config_data = load_config(config_path)
    except TodoJournalError as e:
        logger.error(f"Ошибка загрузки конфигурации: {e.message}")
        print(e.message)
        sys.exit(1)

    # Если в конфиге нет журналов, предложим создать первый
    if not config_data["journals"]:
        # Показать диалог создания журнала (можно вынести в функцию)
        from tkinter import Tk, messagebox, simpledialog, filedialog
        root = Tk()
        root.withdraw()
        if messagebox.askyesno("Первый запуск", "У вас нет ни одного журнала. Создать первый?"):
            name = simpledialog.askstring("Название", "Введите название журнала:")
            if name:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json")],
                    initialfile=f"todo_{name}.json",
                    title="Сохранить журнал"
                )
                if file_path:
                    TodoJournal.create(file_path, name)
                    config_data = add_journal(config_data, name, file_path)
                    config_data = set_current_journal(config_data, name)
                    save_config(config_data, config_path)
                else:
                    logger.info("Создание журнала отменено")
                    return
            else:
                logger.info("Создание журнала отменено")
                return
        else:
            logger.info("Пользователь не захотел создавать журнал")
            return
        root.destroy()

    # Получаем путь к текущему журналу
    current_name = config_data.get("current_journal")
    if not current_name:
        # Если нет текущего, но есть журналы, выбираем первый
        current_name = next(iter(config_data["journals"].keys()), None)
        if current_name:
            config_data = set_current_journal(config_data, current_name)
            save_config(config_data, config_path)
        else:
            logger.error("Нет доступных журналов")
            sys.exit(1)

    journal_path = config_data["journals"][current_name]

    # Создаём объект TodoJournal
    try:
        journal = TodoJournal(journal_path)
    except TodoJournalError as e:
        logger.error(f"Ошибка открытия журнала: {e.message}")
        messagebox.showerror("Ошибка", f"Не удалось открыть журнал:\n{e.message}")
        sys.exit(1)

    # Запуск GUI – передаём конфигурацию
    app = MainWindow(journal, config_data, config_path)
    app.mainloop()
    logger.info("Приложение завершено")

if __name__ == "__main__":
    main()