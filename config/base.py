# -*- coding: utf-8 -*-
import os

import logging
from pathlib import Path

"""
基础配置
"""


class BaseConfig(object):
    SECRET_KEY = '*this-really_needs-to-be-changed*'

    DEBUG = False
    TESTING = False

    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent.absolute()

    REDIS_URL = ""

    ELASTICSEARCH_URL = ""

    # SQLITE
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(PROJECT_ROOT / "app-dev.db")
    # 是否在每次更新数据库时给出提示（追踪修改）
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 是否开启权限鉴定
    IS_AUTH_ENABLED = False

    # 发生 error 时邮件通知 ADMINS
    IS_ERROR_MAIL_ENABLED = False

    LOG_LEVEL = logging.DEBUG

    ADMINS = ['xiaoyin_c@qq.com']

    # api 版本，1
    API_VERSION = '1'

    # 为 flask-rest-api 指定遵守的 openapi 版本
    OPENAPI_VERSION = '3.0.2'

    # base path for json file and ui
    OPENAPI_URL_PREFIX = '/api/v1'
    OPENAPI_JSON_PATH = "/openapi.json"  # openapi spec json path

    API_SPEC_OPTIONS = {
        "info": {
            "title": "拆小鹤",
            "description": "小鹤音形拆字、赛文、成绩记录系统 RESTFul API - Version 1",
            "contact": {
                "email": "xiaoyin_c@qq.com",
                "url": "https://github.com/ryan4yin/xhup-club-api",
            },
            "license": {
                "name": "MIT Licence",
                "url": "https://github.com/ryan4yin/xhup-club-api/blob/master/LICENSE"
            }
        },
        "components": {
            "securitySchemes": {
                "api_key": {
                    "description": "更好的方案是再添加一个 secret-key，用于对数据做签名校验",
                    "type": "apiKey",
                    "name": "api_key",
                    "in": "header"
                }
            },
        }
    }

    # redoc api doc
    OPENAPI_REDOC_PATH = '/redoc'

    # swagger-ui api doc
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_VERSION = '3.20.8'  # 用于生成静态文件的 cdn 链接
    OPENAPI_SWAGGER_UI_SUPPORTED_SUBMIT_METHODS = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch']

