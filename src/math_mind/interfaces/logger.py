from abc import ABC, abstractmethod


class Logger(ABC):
    """Interface for structured logging throughout the application."""

    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        raise NotImplementedError


class LoggerProvider(ABC):
    """Interface for creating Logger instances. Swap implementations to change logging backend."""

    @abstractmethod
    def get_logger(self, name: str) -> Logger:
        raise NotImplementedError
