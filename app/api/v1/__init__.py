# -*- coding: utf-8 -*-
from flask_rest_api import Api

from .session import *
from .user import *
from .xhup import *


""""
拆小鹤 RESTFul API - Version 1
"""


def init_api(api_: Api):
    # 要将 flask-rest-api 定义的 blueprint 注册到 api_rest
    api_.register_blueprint(session_bp)
    api_.register_blueprint(user_bp)
    api_.register_blueprint(xhup_bp)
