# -*- coding: utf-8 -*-
from flask_rest_api import Api


# 这里的问题是，blueprint 被 flask-rest-api 用来区分资源了
# 而 blueprint 是不能嵌套的，因此没有办法直接给 api 模块指定 url_prefix
# 还是说有这样的方法，只是我不晓得？
api_prefix = "/api/v1"

from app.api.session import *
from app.api.users import *
from app.api.xhup import *


""""
拆小鹤 RESTFul API - Version 1
"""


def init_api(api_: Api):
    # 要将 flask-rest-api 定义的 blueprint 注册到 api_rest
    api_.register_blueprint(session_bp)
    api_.register_blueprint(user_bp)
    api_.register_blueprint(xhup_bp)
