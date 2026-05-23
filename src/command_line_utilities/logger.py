import abc
import dataclasses
import datetime
import logging

class Logger(abc.ABC):
    MULTIPROCESSING: bool = False
    INSTANCES: dict[str, "Logger"] = {}
    TAGS: list[str] = []

    @staticmethod
    def get(name: str) -> "Logger":
        if name not in Logger.INSTANCES:
            constructor = QueueLogger if Logger.MULTIPROCESSING else LoggingLogger
            Logger.INSTANCES[name] = constructor(name)

        return Logger.INSTANCES[name]

    def __init__(self, name: str):
        self.name = name

    def debug(self, msg: str, *args, **kwargs):
        self.log_at_level(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self.log_at_level(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.log_at_level(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.log_at_level(logging.ERROR, msg, *args, **kwargs)

    def fatal(self, msg: str, *args, **kwargs):
        self.log_at_level(logging.FATAL, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.log_at_level(logging.CRITICAL, msg, *args, **kwargs)

    def log_at_level(self, level: int, msg: str, *args, **kwargs):
        for tag in Logger.TAGS:
            msg = f'{msg} [{tag}]'
        for tag in kwargs.pop('tags', []):
            msg = f'{msg} [{tag}]'
        self.log_at_level_impl(level, msg, *args, **kwargs)

    @abc.abstractmethod
    def log_at_level_impl(self, level: int, msg: str, *args, **kwargs):
        ''' '''


class LoggingLogger(Logger):

    def __init__(self, name: str):
        super().__init__(name)
        logger = logging.getLogger(name)
        self.level_to_function = {
            logging.DEBUG: logger.debug,
            logging.INFO: logger.info,
            logging.WARNING: logger.warning,
            logging.ERROR: logger.error,
            logging.FATAL: logger.fatal,
            logging.CRITICAL: logger.critical,
        }

    def log_at_level_impl(self, level: int, msg: str, *args, **kwargs):
        logger_function = self.level_to_function[level]
        logger_function(msg, *args, **kwargs)


class QueueLogger(Logger):

    @dataclasses.dataclass
    class SimpleLogRecord:
        timestamp: datetime.datetime
        name: str
        level: int
        msg: str
        args: tuple
        kwargs: dict

    QUEUE: list[SimpleLogRecord] = []

    def __init__(self, name: str):
        super().__init__(name)

    def log_at_level_impl(self, level: int, msg: str, *args, **kwargs):
        record = self.SimpleLogRecord(timestamp = datetime.datetime.now(),
                                      name = self.name,
                                      level = level,
                                      msg = msg,
                                      args = args,
                                      kwargs = kwargs)
        QueueLogger.QUEUE.append(record)
