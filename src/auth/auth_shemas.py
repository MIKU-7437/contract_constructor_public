"""Available params: 'type':(class,), 'min_length':int, 'max_length':int, 'default': any, 'uuid4': True, 'email': True"""
from shared.base_input_dto import BaseDTO


class DemoDTO(BaseDTO):
    """Anonymous user data"""


class RegisterDTO(BaseDTO):
    login = {'type': (str,), 'min_length': 4, 'max_length': 30}
    password = {'type': (str,), 'min_length': 5, 'max_length': 300}
    email = {'type': (str,), 'email': True}
    name = {'type': (str,), 'min_length': 3, 'max_length': 30}


class LoginDTO(BaseDTO):
    login = {'type': (str,), 'min_length': 4, 'max_length': 30}
    password = {'type': (str,), 'min_length': 5, 'max_length': 300}


class RefreshDTO(BaseDTO):
    refresh = {'type': (str,), 'uuid4': True}


class LogoutDTO(BaseDTO):
    user_id = {'type': (int,)}
    session_id = {'type': (str,)}
