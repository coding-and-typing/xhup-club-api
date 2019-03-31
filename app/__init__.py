import logging
from datetime import timedelta

import os

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_rest_api import Api
from flask_redis import Redis
from flask_rq2 import RQ
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from flask_mail import Mail
from flask_sockets import Sockets
from werkzeug.contrib.fixers import ProxyFix

from config import config_by_name, BaseConfig

# 获取环境
env = os.getenv("XHUP_ENV")
current_config: BaseConfig = config_by_name[env]
logging.basicConfig(level=current_config.LOG_LEVEL)  # 日志

# 初始化 flask 的各个插件
db = SQLAlchemy()
migrate = Migrate()
redis = Redis()  # 用于短信验证码等信息的存储
rq = RQ()  # 用于任务队列

login_manager = LoginManager()
mail = Mail()
sockets = Sockets()

cors = CORS()  # REST API 允许跨域
api_rest = Api()

# ip 访问频率限制
limiter = Limiter(key_func=get_remote_address)


def create_app():
    app = Flask(__name__)
    app.config.from_object(current_config)

    # 允许 /api/ 下的 api 跨域访问
    cors.init_app(app, resources={r"/api/*": {
        "origins": "*",
        "max_age": timedelta(days=1),
        "supports_credentials": True,  # 允许跨域使用 cookie
    }})

    # 将各 flask 插件注册到 app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    sockets.init_app(app)
    api_rest.init_app(app)

    # ip 访问频率限制
    # 1. 如果 flask 跑在 proxy server 后面（比如 nginx），就需要用 ProxyFix
    # app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=1)
    limiter.init_app(app)
    for handler in app.logger.handlers:  # 为 limiter 添加日志处理器
        limiter.logger.addHandler(handler)

    # TODO elasticsearch 模糊搜索
    # app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    #     if app.config['ELASTICSEARCH_URL'] else None

    redis.init_app(app, config_prefix="REDIS0")  # 使用 REDIS0_URL

    # TODO 使用 rq 实现异步任务
    rq.init_app(app)

    # 注册 rest api 模块，
    from app import api as api_v1
    api_v1.init_api(api_rest)  # 注意是使用已经在 app 上注册了的 app_rest

    # Import Sockets events so that they are registered with Flask-Sockets
    from . import events
    events.init_websockets(sockets)

    app.logger.info('拆小鹤后台系统开始启动～ hhh')
    return app


from . import models  # Import SQLAlchemy models