import os

import logging
import rq

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

from elasticsearch import Elasticsearch
from redis import Redis

from config import config_by_name

logger = logging.getLogger(__name__)


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()


def init_app():
    app = Flask(__name__)

    env = os.getenv("XHUP_ENV")
    app.config.from_object(config_by_name[env])

    db.init_app(app)
    migrate.init_app(app)
    login.init_app(app)
    mail.init_app(app)

    # TODO 使用消息队列实现异步任务
    # TODO elasticsearch 模糊搜索
    # app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    #     if app.config['ELASTICSEARCH_URL'] else None
    # app.redis = Redis.from_url(app.config['REDIS_URL'])
    # app.task_queue = rq.Queue('xhup-tasks', connection=app.redis)


