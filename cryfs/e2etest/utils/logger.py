from typing import List
import attr
from functools import reduce
from enum import Enum


class LogLevel(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4

    def to_string(self) -> str:
        return {
            LogLevel.INFO: "INFO",
            LogLevel.WARNING: "WARNING",
            LogLevel.ERROR: "ERROR",
            LogLevel.FATAL: "FATAL",
        }[self]


@attr.s(auto_attribs=True)
class LogEntry(object):
    level: LogLevel = LogLevel.INFO
    message: str = ""

    def to_string(self) -> str:
        return "[%s] %s" % (self.level.to_string(), self.message)


class Logger(object):
    def __init__(self) -> None:
        self._log: List[LogEntry] = []

    def log(self, level: LogLevel, message: str) -> None:
        self._log.append(LogEntry(level=level, message=message))

    def to_string(self) -> str:
        return reduce(lambda s, i: s + i.to_string() + "\n", self._log, "")
