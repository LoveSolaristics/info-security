from logging import getLogger, DEBUG, FileHandler, Formatter, Logger


class LogManager:
    def __init__(self):
        self.logger = getLogger('messenger-api')
        self.handler = FileHandler('api_logs.txt', mode='a',
                                   encoding='utf-8')
        self.basic_formatter = Formatter(
            "%(asctime)s %(levelname)s %(message)s")

        self.logger.setLevel(DEBUG)
        self.handler.setLevel(DEBUG)
        self.handler.setFormatter(self.basic_formatter)
        self.logger.addHandler(self.handler)

    @property
    def get_log(self) -> Logger:
        return self.logger

    def log_error(self, error: Exception) -> None:
        # задаём новый формат записи в лог
        err_formatter = Formatter(
            f"%(asctime)s %(levelname)s %(message)s {error=}")
        self.handler.setFormatter(err_formatter)
        self.logger.addHandler(self.handler)

        self.logger.error(error)  # записываем сообщение

        # возвращаемся к старым настройкам
        self.handler.setFormatter(self.basic_formatter)
        self.logger.addHandler(self.handler)
