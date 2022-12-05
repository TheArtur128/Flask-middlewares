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


class ErrorJSONResponseFormatter(ErrorHandler, ABC):
    def _handle_error(self, error: Exception) -> any:
        response = jsonify(self._get_response_body_from(error))
        response.status_code = jsonify(self._get_status_code_from(error))

        return response

    @abstractmethod
    def _get_response_body_from(self, error: Exception) -> dict:
        pass

    @abstractmethod
    def _get_status_code_from(self, error: Exception) -> int:
        pass


class TemplatedErrorJSONResponseFormatter(ErrorJSONResponseFormatter, ABC):
    def __init__(self, is_format_message: bool = True, is_format_type: bool = False):
        self.is_format_message = is_format_message
        self.is_format_type = is_format_type

    def _get_response_body_from(self, error: Exception) -> dict:
        response_body = dict()

        if self.is_format_message:
            response_body['message'] = self._get_error_message_from(error)

        if self.is_format_type:
            response_body['error-type'] = self._get_error_type_name_from(error)

        return response_body

    def _get_error_message_from(self, error: Exception) -> str:
        return str(error)

    def _get_error_type_name_from(self, error: Exception) -> str:
        return type(error).__name__
