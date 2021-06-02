# -*- coding: utf-8 -*-
from flask_smorest import Api
from flask_smorest import Blueprint

from app import limiter

""""
拆小鹤 RESTFul API - Version 1

# 这里的问题是，blueprint 被 flask-rest-api 用来区分资源了
# 而 blueprint 是不能嵌套的，因此没有办法直接给 api 模块指定 url_prefix
# 还是说有这样的方法，只是我不晓得？
"""


api_prefix = "/api/v1"

article_bp = Blueprint(
    'article', __name__, url_prefix=f'{api_prefix}/article',
    description="文章库的增删查改（待实现）"
)
table_bp = Blueprint(
    'characters', __name__, url_prefix=f'{api_prefix}/characters',
    description="拆字表相关"
)
comp_article_bp = Blueprint(
    'comp_article', __name__, url_prefix=f'{api_prefix}/comp_article',
    description="（各群组）赛文的增删查改"
)
relation_bp = Blueprint(
    'relation', __name__, url_prefix=f'{api_prefix}/relation',
    description="用户与群组的绑定（建立 relation）"
)
session_bp = Blueprint(
    'session', __name__, url_prefix=f'{api_prefix}/session',
    description="用户的登入登出，看作 session 的创建与删除"
)
user_bp = Blueprint(
    'user', __name__, url_prefix=f'{api_prefix}/user',
    description="用户的注册、用户信息的获取与修改"
)


def init_api(api_: Api):
    limiter.limit("666/hour;20/minute;3/second")(table_bp)  # 更严格的限制

    # 要将 flask-rest-api 定义的 blueprint 注册到 api_rest
    api_.register_blueprint(article_bp)
    api_.register_blueprint(comp_article_bp)
    api_.register_blueprint(table_bp)
    api_.register_blueprint(relation_bp)
    api_.register_blueprint(session_bp)
    api_.register_blueprint(user_bp)
