# -*- coding: utf-8 -*-
import os

import logging
from pathlib import Path
from typing import List

import yaml
from pydantic.networks import HttpUrl, RedisDsn, EmailStr
from pydantic import BaseSettings

basedir = Path(__file__).parent.resolve()


class Config(BaseSettings):
    # 1. flask 相关配置
    SECRET_KEY: str

    # Flask - Whether debug mode is enabled. When using ``flask run`` to start
    #         the development server, an interactive debugger will be shown for
    #         unhandled exceptions, and the server will be reloaded when code
    #         changes.
    DEBUG: bool = False
    # Flask - disable error catching during request handling, to get better error reports
    TESTING: bool = False

    # 项目根目录
    PROJECT_ROOT: Path = basedir

    # 2. 数据库相关配置
    ELASTICSEARCH_URL: str
    # SQLite
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'  # 默认使用内存数据库，就是说每次运行都是全新数据库
    # 是否在每次更新数据库时给出提示（追踪修改）
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = True

    # 3. 权限与日志配置
    # 是否开启权限鉴定
    IS_AUTH_ENABLED: bool = False

    # 发生 error 时邮件通知 ADMINS
    IS_ERROR_MAIL_ENABLED: bool = False
    LOG_LEVEL: int = logging.DEBUG
    ADMINS: List[EmailStr] = ['xiaoyin_c@qq.com']

    # 授权 TOKEN
    BOT_TOKEN: str

    # 各种过期时间（expires）
    VERIFICATION_CODE_EXPIRES: int = 3 * 60  # 验证码过期时间，3 分钟

    # 6. 群聊相关配置
    # 图灵聊天 api
    TURING_API: HttpUrl = "http://openapi.tuling123.com/openapi/api/v2"
    TURING_KEY: str

    # xhup.club 短链 api
    SHORT_URL_API: HttpUrl = 'http://xhup.club/index.php/Home/Service/getShortUrl'
    SHORT_URL_TOKEN: str

    # redis 相关配置
    REDIS0_URL: RedisDsn = "redis://localhost:6379/0"  # 短信验证码等数据用 db 0 （flask-and-redis）
    RQ_REDIS_URL: RedisDsn = "redis://localhost:6379/1"  # 任务队列用 db 1 （flask-rq2）

    # 各种 redis key 的格式串
    CAPTCHA_FORMAT: str = "captcha:{}"  # 登录验证码对应的 key
    GROUP_BIND_VERI_FORMAT: str = "group_user_relation:{}"  # 群组绑定验证码对应的 key
    RESET_PASSWORD_VERI_FORMAT: str = "reset_password:{}"  # 重设密码对应的验证码

    # ========================================================
    # 如下为静态配置内容（hardcoded）
    # ========================================================

    # ip 频率限制（默认策略）
    RATELIMIT_DEFAULT = "900/hour;30/minute;3/second"

    # 4. flask-rest-api 相关配置
    # api 版本，1
    API_VERSION = '1'

    # 默认的分页参数
    DEFAULT_PAGINATION_PARAMETERS = {'page': 1, 'page_size': 25, 'max_page_size': 1000}

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
                    "type": "apiKey",
                    "name": "X-API-Key",
                    "in": "header"
                },
                'jwt': {
                    'bearerFormat': 'JWT',
                    'scheme': 'bearer',
                    'type': 'http'
                }
            },
        }
    }

    # redoc api doc
    OPENAPI_REDOC_PATH = '/redoc'

    # swagger-ui api doc
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_SWAGGER_UI_URL = "https://cdn.bootcss.com/swagger-ui/3.23.11/"

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

    # 允许出现的单字
    CHARS_ALLOWED = frozenset((PROJECT_ROOT / "data/小鹤全部单字.txt").read_text(encoding='utf-8'))
    CHARS_TOP_1500 = (PROJECT_ROOT / "data/常用单字前1500.txt").read_text(encoding='utf-8')
    CHARS_TOP_500 = CHARS_TOP_1500[:500]  # 前五百
    CHARS_MIDDLE_500 = CHARS_TOP_1500[500:1000]  # 中五百
    CHARS_LAST_500 = CHARS_TOP_1500[1000:]  # 后五百
    assert len(frozenset(CHARS_TOP_1500)) == len(CHARS_TOP_1500) == 1500

    # 字体路径（用于验证码生成）
    FONTS_PATH = [str(p) for p in (PROJECT_ROOT / "data/fonts").iterdir()]


config_yaml_path = Path(os.getenv("CONFIG_PATH", basedir / "test-config.yaml"))
print(f"using config: {config_yaml_path}", flush=True)

config_dict = yaml.safe_load(config_yaml_path.read_text(encoding="utf-8")) or dict()
current_config = Config(**config_dict)  # get config from config_dict & environment variables
