import sys
from src.config import load_config, get_config_path
from src.logger import setup_logging, get_logger
from src.exceptions import TodoJournalError
from src.todo_journal import TodoJournal

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
        print("Текущий журнал не задан. Используйте настройки для выбора.")
        # Пока завершаем
        return

    # Создаём объект TodoJournal
    try:
        journal = TodoJournal(journal_path)
    except TodoJournalError as e:
        logger.error(f"Ошибка открытия журнала: {e.message}")
        print(e.message)
        sys.exit(1)

    #TODO: запуск GUI
    print("Запуск GUI пока не реализован")
    logger.info("Приложение завершено")

if __name__ == "__main__":
    main()