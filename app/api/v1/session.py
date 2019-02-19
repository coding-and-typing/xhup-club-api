# -*- coding: utf-8 -*-
import logging
import typing

from flask.views import MethodView
from flask_login import current_user, login_user, logout_user, login_required
import marshmallow as ma
from flask_rest_api import abort, Blueprint

from app import api_rest
from app.models import User

logger = logging.getLogger(__name__)

session_bp = Blueprint(
    'session', __name__, url_prefix='/api/v1',
    description="用户的登入登出"
)


@api_rest.definition('Session')
class SessionSchema(ma.Schema):
    """应该暴露给 API 的 Session 属性
    """
    class Meta:
        strict = True
        ordered = True

    id = ma.fields.Int(dump_only=True)
    username = ma.fields.String()
    email = ma.fields.Email()


class SessionCreateArgsSchema(ma.Schema):
    """请求应该带有的参数

    """
    class Meta:
        strict = True
        ordered = True

    username = ma.fields.String()
    password_hash = ma.fields.String()


@session_bp.route('/session/')
class SessionView(MethodView):
    """登录与登出
    将登录与登出看作是对 session 的创建与删除
    """

    @session_bp.arguments(SessionCreateArgsSchema)
    @session_bp.response(code=201)
    def post(self, data: typing.Dict):
        """用户登录
        暂时使用 cookie 保存登录状态
        ---
        :param data:
        :return:
        """
        # 验证登录
        user = User.query.filter_by(username=data['username']).first()
        if user is not None \
                and user.check_password(data['password_hash']):
            login_user(user)
        else:
            abort(401, message='error username or password')

    @session_bp.response(SessionSchema, code=200)
    @login_required
    def get(self):
        """获取当前用户信息

        ---
        :return:
        """
        return current_user

    @session_bp.response(code=204)
    @login_required
    def delete(self):
        """用户登出
        ---
        :return:
        """
        logout_user()  # 不需要参数，它自己就能查到 current_user

