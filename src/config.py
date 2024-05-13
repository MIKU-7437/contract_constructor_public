import os
from pathlib import Path

from dotenv import load_dotenv, find_dotenv


ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')


if ENVIRONMENT == 'dev':
    load_dotenv(find_dotenv(f'.env.{ENVIRONMENT}'))

DEBUG = bool(os.getenv('DEBUG', None))

PUBLIC_HOST = os.getenv('PUBLIC_HOST', 'http://localhost:8000')

BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR.joinpath('media')

DB_HOST = os.getenv('DB_HOST', None)
DB_PORT = os.getenv('DB_PORT', None)
DB_NAME = os.getenv('DB_NAME', None)
DB_USER = os.getenv('DB_USER', None)
DB_PASS = os.getenv('DB_PASS', None)
DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


JWT_SECRET = os.getenv('JWT_SECRET', None)
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', None)
JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', None))
REFRESH_EXPIRATION = int(os.getenv('REFRESH_EXPIRATION', None))
HASH_SALT = os.getenv('HASH_SALT', None)

PASSWORD_CHANGE_KEY = os.getenv('PASSWORD_CHANGE_KEY', None)

DEMO_USER_EXPIRATION = int(os.getenv('DEMO_USER_EXPIRATION', None))
TEMP_FILES_EXPIRATION = int(os.getenv('TEMP_FILES_EXPIRATION', None))


API_V1 = '/api/v1'
