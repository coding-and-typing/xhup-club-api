import os

from flask import Flask
from flask_rest_api import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from flask_mail import Mail
from flask_socketio import SocketIO

from config import config_by_name

db = SQLAlchemy()
migrate = Migrate()

login = LoginManager()
mail = Mail()
socketio = SocketIO()

api_rest = Api()

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
    socketio.init_app(app)
    api_rest.init_app(app)

    # TODO elasticsearch 模糊搜索
    # app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    #     if app.config['ELASTICSEARCH_URL'] else None

    # TODO 使用消息队列实现异步任务
    # app.redis = Redis.from_url(app.config['REDIS_URL'])
    # app.task_queue = rq.Queue('xhup-tasks', connection=app.redis)

    # Import Socket.IO events so that they are registered with Flask-SocketIO
    from . import events
    events.init_app(app)

    # 注册 rest api 模块，
    from app import api as api_v1
    api_v1.init_api(api_rest)  # 注意是使用已经在 app 上注册了的 app_rest

    # 日志
    app.logger.setLevel(current_config.LOG_LEVEL)
    app.logger.info('拆小鹤后台系统开始启动～ hhh')
    return app


from . import models  # Import SQLAlchemy models