import traceback
from abc import abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth_shemas import BaseDTO
from shared.error_structure import Error


class ResponseFailure:
    def __init__(self, errors, http_code: int = None):
        self.__errors = errors
        self.__http_error = http_code

    @property
    def http_error(self) -> int:
        return self.__http_error

    @property
    def errors(self) -> list[str]:
        return [x.dict for x in self.__errors]

    def __bool__(self) -> bool:
        return False


class ResponseSuccess:
    def __init__(self, data):
        self.data = data

    def __bool__(self) -> bool:
        return True


class BaseUC:
    """Base class for working with use cases and their errors"""
    ReqDTO: BaseDTO = BaseDTO
    Error: Error = Error

    def __init__(self, input_data: dict, session: AsyncSession):
        self.session = session
        self.__http_error: int = 500
        self.__errors: list[Error] = []
        self.__input_data = self.ReqDTO(input_data)

    async def exec(self) -> ResponseSuccess | ResponseFailure:
        return await self.__handler()

    async def __handler(self) -> ResponseSuccess | ResponseFailure:

        if self.__input_data.has_errors:
            return ResponseFailure(errors=self.__input_data.get_result(), http_code=406)

        try:
            success_response = await self.process_request(self.__input_data)
        except Exception as exc:
            traceback.print_exc(limit=7)
            message = exc.message if hasattr(exc, 'message') else str(exc)
            error = self.Error(error_type='system_error', message=message)
            return ResponseFailure(errors=[error], http_code=500)

        if self.__errors:
            return ResponseFailure(errors=self.__errors, http_code=self.__http_error)

        return ResponseSuccess(data=success_response)

    def add_error(self, *args, **kwargs):
        """Adding a new error object to error storage"""
        http_code = kwargs.get('http_code', None)
        if http_code is not None and isinstance(http_code, int):
            self.__http_error = http_code
        self.__errors.append(Error(*args, **kwargs))

    def add_errors(self, errors: list[Error], http_code: int = None):
        """Adding a new error object to error storage"""
        if http_code is not None and isinstance(http_code, int):
            self.__http_error = http_code
        self.__errors.extend(errors)

    @abstractmethod
    async def process_request(self, req_dto):
        pass
