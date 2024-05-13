from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from passlib.context import CryptContext
from config import JWT_EXPIRATION, JWT_ALGORITHM, JWT_SECRET, HASH_SALT
from shared.time_utils import now_utc


def check_password(pwd: str, pwd_hash: str) -> bool:
    """Сопоставить пароль с хешем"""
    salted_pwd = ''.join([pwd, HASH_SALT])
    encrypter = CryptContext(schemes=['md5_crypt'])
    return encrypter.verify(salted_pwd, pwd_hash)


def get_hash(pwd: str) -> str:
    """Получить хеш соленого пароля"""
    salted_pwd = ''.join([pwd, HASH_SALT])
    encrypter = CryptContext(schemes=['md5_crypt'])
    hash_result = encrypter.hash(salted_pwd)
    return hash_result


def get_jwt_token(data: dict) -> str:
    """Сгенерировать jwt токен с полезной нагрузкой"""
    expiration = now_utc() + timedelta(seconds=JWT_EXPIRATION)
    data.update({'exp': expiration})
    token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def get_refresh_token():
    return str(uuid4())


def check_jwt_token(token: str) -> dict | None:
    """Декодировать jwt токен и проверить его expiration"""
    try:
        decoded_data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        decoded_data['exp'] = datetime.fromtimestamp(decoded_data['exp']).astimezone(timezone.utc)
        if now_utc() < decoded_data['exp']:
            return decoded_data
    except jwt.PyJWTError:
        return
