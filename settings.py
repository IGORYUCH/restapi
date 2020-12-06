from datetime import timedelta
from os import urandom


class BaseConfig:
    SECRET_KEY = 'I like anime'
    JWT_AUTH_URL_RULE = '/restapi/users/login'
    JWT_EXPIRATION_DELTA = timedelta(hours=2)
    DB_NAME = 'restapi3'
    DB_USER = 'postgres'
    DB_PASSWORD = '123q'
    DB_PORT = 5432
    DB_HOST = 'localhost'
    USERSTABLE = 'users'
    TASKSTABLE = 'tasks'


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    JWT_EXPIRATION_DELTA = timedelta(minutes=30)
    SECRET_KEY = urandom(128)
