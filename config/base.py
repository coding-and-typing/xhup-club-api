# -*- coding: utf-8 -*-
import os

import logging
from pathlib import Path

"""
基础配置
"""


class BaseConfig(object):
    # 1. flask 相关配置
    SECRET_KEY = '*this-really_needs-to-be-changed*'

    DEBUG = False
    TESTING = False

    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent[1].absolute()

    # 2. 数据库相关配置
    REDIS_URL = ""
    ELASTICSEARCH_URL = ""
    # SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(PROJECT_ROOT / "app-dev.db")
    # 是否在每次更新数据库时给出提示（追踪修改）
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 3. 权限与日志配置
    # 是否开启权限鉴定
    IS_AUTH_ENABLED = False

    # 发生 error 时邮件通知 ADMINS
    IS_ERROR_MAIL_ENABLED = False
    LOG_LEVEL = logging.DEBUG
    ADMINS = ['xiaoyin_c@qq.com']

    # 4. flask-rest-api 相关配置
    # api 版本，1
    API_VERSION = '1'

    # 指定遵守的 openapi 版本
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

    # 5. 赛文系统相关配置
    # 随机赛文，使用每日一文的 api（注意抓取频率，毕竟人家也是公益网站。）
    # 另外这个网站的标点处理得也不彻底，需要自己筛选。
    DAILY_ARTICLE_API = "https://meiriyiwen.com/"
    RANDOM_ARTICLE_API = f"{DAILY_ARTICLE_API}/random"
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"

    # 小拆五笔
    CHAIWUBI_URL = "http://www.chaiwubi.com/match/"  # 仅在登录后，用于获取赛文列表
    CHAIWUBI_API = "http://47.93.35.203/saiwen/json.php"  # 登录、赛文添加/修改/删除

    # 6. 群聊相关配置
    # 图灵聊天 api
    TURING_API = "http://openapi.tuling123.com/openapi/api/v2"
    TURING_KEY = os.getenv("TURING_KEY")

    # xhup.club 短链 api
    SHORT_URL_API = 'http://xhup.club/index.php/Home/Service/getShortUrl'
    SHORT_URL_TOKEN = os.getenv("SHORT_URL_TOKEN")

    # 授权 TOKEN
    BOT_TOKEN = 'test_token'

    # ip 频率限制（默认策略）
    RATELIMIT_DEFAULT = "900/hour;30/minute;3/second"
