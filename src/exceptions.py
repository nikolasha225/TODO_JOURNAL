#Исключения для TodoJournal

import textwrap
from typing import Optional


#Базовое исключение для TodoJournal
class TodoJournalError(Exception):

    def __init__(self, error_type: str, **kwargs: str) -> None:
        self.error_type = error_type
        self.message = self._get_error_message(**kwargs)
        super().__init__(self.message)

    #Сообщение об ошибке в зависимости от типа
    def _get_error_message(self, **kwargs: str) -> str:
        messages = {
            "ConfigDirectoryIsFile": """
                Путь до каталога с конфигом является файлом.

                {config_directory_path}

                Удалите файл или укажите другой путь до конфигурационного файла.
            """,
            "ConfigNotFound": """
                Конфигурационный файл не найден и не может быть создан.

                {config_path}

                Проверьте права доступа или создайте файл вручную.
            """,
            "TodoJournalFormatError": """
                Ошибка в формате файла журнала:

                Имя журнала: {journal_name}
                Путь до журнала: {journal_path}

                Ожидается JSON с ключами "name" и "todos".
            """,
        }

        msg = messages.get(self.error_type, "Неизвестная ошибка.")
        # Подставляем переданные параметры
        if kwargs:
            msg = msg.format(**kwargs)
        # Убираем лишние отступы для красивого вывода
        msg = textwrap.dedent(msg).strip()
        return msg