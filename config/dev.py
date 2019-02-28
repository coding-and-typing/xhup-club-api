# -*- coding: utf-8 -*-
import os
from urllib import parse

from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    DEBUG = True

    # PostgreSQL
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = parse.quote_plus(os.getenv("DB_PASSWORD", ""))
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}'.format(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        name=DB_NAME,
    )


