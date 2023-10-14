from loguru import logger as loguru_logger


class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = cls._create_logger()
        return cls._instance

    @classmethod
    def _create_logger(cls):
        return loguru_logger


def get_logger():
    return Logger()
