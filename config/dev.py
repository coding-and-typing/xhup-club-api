# -*- coding: utf-8 -*-
import os
from urllib import parse

from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    DEBUG = True

    # PostgreSQL
    # DB_USER = 'ryan'
    # DB_PASSWORD = ''
    # DB_NAME = 'http_api'
    # DB_HOST = 'localhost'
    # DB_PORT = '5432'
    # SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}'.format(
    #     user=DB_USER,
    #     password=DB_PASSWORD,
    #     host=DB_HOST,
    #     port=DB_PORT,
    #     name=DB_NAME,
    # )


