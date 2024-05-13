import uuid
from shared.error_structure import Error


class BaseDTO:
    """Base validation class, collecting errors."""

    def __init__(self, args: dict):
        self.__data_storage: dict = args
        self.__errors: list[Error] = []

        self.__main_validator()

        if self.has_errors:
            setattr(self, 'errors', self.__errors)
        else:
            for attr in self.__class__.as_dict():
                setattr(self, attr, self.__data_storage[attr])

    @property
    def has_errors(self):
        """Returns True if Base validator found any errors"""
        return bool(len(self.__errors))

    def get_result(self) -> dict | list[Error]:
        if self.has_errors:
            result = self.__errors
        else:
            result = {}
            for x in self.__class__.as_dict():
                result.update({x: self.__data_storage[x]})
        return result

    def __bool__(self):
        return not self.has_errors

    def _add_error(self, error: Error):
        self.__errors.append(error)

    @classmethod
    def as_dict(cls) -> dict:
        """Returns a dict with public attributes which contains fields parameters"""
        attrs_and_methods = dir(cls)

        without_magic = []
        for method in attrs_and_methods:
            if not method.startswith('_'):
                without_magic.append(method)

        attrs_only = []
        for method in without_magic:
            if not callable(getattr(cls, method)) and not isinstance(getattr(cls, method), property):
                attrs_only.append(method)

        result = {}
        for method in attrs_only:
            result[method] = getattr(cls, method)

        return result

    def __main_validator(self):
        """Step by step checking every field on accepted parameters"""
        error = self.__check_data_type()
        if error:
            self._add_error(error)
            return

        specified_fields = self.as_dict()
        for field, params in specified_fields.items():
            error = self.__check_required_field(field, params)
            if error:
                self._add_error(error)
                continue

            error = self.__check_field_type(field, params)
            if error:
                self._add_error(error)
                continue

            error = self.__check_max_length(field, params)
            if error:
                self._add_error(error)
                continue

            error = self.__check_min_length(field, params)
            if error:
                self._add_error(error)
                continue

            error = self.__check_list(field, params)
            if error:
                self._add_error(error)
                continue

            error = self.__check_email(field, params)
            if error:
                self._add_error(error)
                continue

            error = self.__check_uuid4(field, params)
            if error:
                self._add_error(error)
                continue

    def __check_data_type(self) -> Error | None:
        if not isinstance(self.__data_storage, dict):
            return Error(error_type='param_error', message='Dictionary expected')

    def __check_required_field(self, field: str, params: dict) -> Error | None:
        if 'default' not in params.keys() and field not in self.__data_storage:
            return Error(error_type='param_error', message='Field is required', location=f'{field}')
        if field not in self.__data_storage:
            self.__data_storage[field] = params.get('default')

    def __check_field_type(self, field: str, params: dict) -> Error | None:
        if isinstance(self.__data_storage[field], params['type']):
            return

        if 'default' in params and params['default'] is None and self.__data_storage[field] is None:
            return

        if 'default' in params and params['default'] is not None and not isinstance(params['default'], params['type']):
            return Error(error_type='system_error', message=f'Wrong schema field', location=f'{field}')

        exp = [param.__name__ for param in params['type']]
        return Error(error_type='param_error', message=f'Wrong type, expected: {exp}', location=f'{field}')

    def __check_max_length(self, field: str, params: dict) -> Error | None:
        if 'max_length' in params \
                and self.__data_storage[field] \
                and len(str(self.__data_storage[field])) > params['max_length']:
            return Error(error_type='param_error', message=f'Max field length {params["max_length"]} simbols', location=f'{field}')

    def __check_min_length(self, field: str, params: dict) -> Error | None:
        if 'min_length' in params \
                and self.__data_storage[field] is not None\
                and len(str(self.__data_storage[field])) < params['min_length']:
            return Error(error_type='param_error', message=f'Min field length {params["min_length"]} simbols', location=f'{field}')

    def __check_list(self, field: str, params: dict) -> Error | None:
        if isinstance(self.__data_storage[field], list) and 'f_level_type' in params:
            for item in self.__data_storage[field]:
                if not isinstance(item, params['f_level_type']):
                    exp = [i.__name__ for i in params['f_level_type']]
                    return Error(error_type='param_error', message=f'Wrong type, expected: {exp}', location=f'{field}')

        if isinstance(self.__data_storage[field], list) and 'f_level_type' not in params:
            return Error(
                error_type='system_error',
                message=f'"f_level_type" - required parameter for list data type',
                location=f'{field}'
            )

    def __check_email(self, field: str, params: dict) -> Error | None:
        if self.__data_storage[field] and 'email' in params:
            value = self.__data_storage[field]
            if '.' not in value or '@' not in value:
                return Error(error_type='param_error', message=f'Incorrect email format', location=f'{field}')

    def __check_uuid4(self, field: str, params: dict) -> Error | None:
        if self.__data_storage[field] and 'uuid4' in params:
            try:
                uuid.UUID(self.__data_storage[field])
            except Exception:
                return Error(error_type='param_error', message=f'Incorrect uuid format', location=f'{field}')
