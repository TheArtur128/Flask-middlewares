from abc import ABC, abstractmethod
from typing import Iterable, Self, Callable


class IErrorHandler(ABC):
    def __call__(self, error: Exception) -> any:
        pass


class ProxyErrorHandler(IErrorHandler):
    def __init__(self, error_handlers: Iterable[IErrorHandler], *, is_return_delegated: bool = True):
        self.error_handlers = tuple(error_handlers)
        self.is_return_delegated = is_return_delegated

    def __call__(self, error: Exception) -> any:
        for error_handler in self.error_handlers:
            result = error_handler(error)

            if self.is_return_delegated and result is not None:
                return result

    @classmethod
    def create_factory_decorator(cls, *args, **kwargs) -> Self:
        def factory_decorator(func: Callable) -> any:
            return cls((func, ), *args, **kwargs)

        return factory_decorator


class ErrorHandler(IErrorHandler, ABC):
    def __call__(self, error: Exception) -> any:
        if self.is_error_correct_to_handle(error):
            return self._handle_error(error)

    @abstractmethod
    def is_error_correct_to_handle(self, error: Exception) -> bool:
        pass

    @abstractmethod
    def _handle_error(self, error: Exception) -> any:
        pass
