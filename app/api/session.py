# -*- coding: utf-8 -*-
import logging
import typing

from flask.views import MethodView
from flask_login import current_user, login_user, logout_user
import marshmallow as ma
from flask_rest_api import abort, Blueprint

from app import api_rest
from app.models import MainUser
from app.utils.common import login_required
from app.api import api_prefix

logger = logging.getLogger(__name__)

session_bp = Blueprint(
    'session', __name__, url_prefix=f'{api_prefix}/session',
    description="用户的登入登出，看作 session 的创建与删除"
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

    username = ma.fields.String(required=True)
    password = ma.fields.String(required=True)
    remember_me = ma.fields.Boolean(required=True)  # 记住我


@session_bp.route('/')
class SessionView(MethodView):
    """登录与登出
    将登录与登出看作是对 session 的创建与删除
    """

    @session_bp.arguments(SessionCreateArgsSchema)
    @session_bp.response(code=201, description="登录成功")
    @session_bp.doc(responses={"401": {'description': "用户名或密码错误"}})
    @session_bp.doc(responses={"400": {'description': "请先登出当前账号"}})
    def post(self, data: typing.Dict):
        """用户登录

        登录成功的响应首部中会带有 Set-Cookie 字段，设置 cookie
        ---
        :param data:
        :return:
        """
        if current_user.is_authenticated:
            abort(400, message="please logout first.")

        # 验证登录
        user = MainUser.query.filter_by(username=data['username']).first()
        if user is not None \
                and user.check_password(data['password']):

            login_user(user, remember=data['remember_me'])

            return user
        else:
            abort(401, message='error username or password')

    @session_bp.response(SessionSchema, code=200, description="成功获取到消息")
    @login_required
    def get(self):
        """获取当前会话（session）信息。

        暂时和 user 的 get 结果一样。（计划返回更多 session 相关的信息）

        需要先登录
        ---
        :return:
        """
        return current_user

    @session_bp.response(code=204, description="Session 删除成功")
    @login_required
    def delete(self):
        """用户登出

        登出后 cookie 失效，需要先登录
        ---
        :return:
        """
        logout_user()  # 不需要参数，它自己就能查到 current_user

