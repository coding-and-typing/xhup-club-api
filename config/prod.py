# -*- coding: utf-8 -*-
import logging
import os

from config import BaseConfig

"""
生产环境配置
"""


class ProductionConfig(BaseConfig):
    SECRET_KEY = os.getenv('XHUP_SECRET_KEY')

    # MySQL
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}:{port}/{name}'.format(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        name=DB_NAME,
    )

    IS_AUTH_ENABLED = True
    IS_ERROR_MAIL_ENABLED = True
    LOG_LEVEL = logging.INFO

