import os

import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO

from elasticsearch import Elasticsearch
from redis import Redis
import rq

from config import config_by_name

logger = logging.getLogger(__name__)


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()
socketio = SocketIO()

# 获取环境
env = os.getenv("XHUP_ENV")
current_config = config_by_name[env]


def create_app():
    app = Flask(__name__)
    app.config.from_object(current_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    # TODO elasticsearch 模糊搜索
    # app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    #     if app.config['ELASTICSEARCH_URL'] else None

    # TODO 使用消息队列实现异步任务
    # app.redis = Redis.from_url(app.config['REDIS_URL'])
    # app.task_queue = rq.Queue('xhup-tasks', connection=app.redis)

    # 注册各项 blueprint
    from .api import v1 as api_v1
    from . import events

    api_v1.init_app(app)
    events.init_app(app)

    app.logger.setLevel(current_config.LOG_LEVEL)

    return app


# Import Socket.IO events so that they are registered with Flask-SocketIO
from . import events

# Import SQLAlchemy models so that they are registered with Flask-SQLAlchemy
from . import models
