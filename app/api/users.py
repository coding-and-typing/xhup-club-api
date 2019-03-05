# -*- coding: utf-8 -*-
import logging
import typing

from flask.views import MethodView
from flask_login import current_user
import marshmallow as ma
from flask_rest_api import abort, Blueprint

from app import api_rest, db
from app.models import MainUser
from app.utils.common import login_required
from app.api import api_prefix

logger = logging.getLogger(__name__)

user_bp = Blueprint(
    'user', __name__, url_prefix=f'{api_prefix}/users',
    description="用户的注册、用户信息的获取与修改"
)


@api_rest.definition('User')
class UserSchema(ma.Schema):
    """应该暴露给 API 的 User 属性
    """
    class Meta:
        strict = True
        ordered = True

    id = ma.fields.Int(dump_only=True)
    username = ma.fields.String()
    email = ma.fields.Email()


class UserCreateArgsSchema(ma.Schema):
    """创建用户需要的参数

    """
    class Meta:
        strict = True
        ordered = True

    username = ma.fields.String(required=True)
    email = ma.fields.Email(required=True)
    password = ma.fields.String(required=True)


@user_bp.route('/')
class UsersView(MethodView):
    """登录与登出

    将登录与登出看作是对 session 的创建与删除
    """

    @user_bp.arguments(UserCreateArgsSchema)
    @user_bp.response(code=201, description="新用户注册成功")
    @user_bp.doc(responses={"400": {'description': "当前已有用户登录，需要先退出登录"}})
    def post(self, data: typing.Dict):
        """用户注册
        ---
        :param data:
        :return:
        """
        if current_user.is_authenticated:
            abort(400, message="you've login, or this account has been used.")
        else:
            user = MainUser(username=data['username'], email=data['email'])
            user.set_password(data['password'])
            db.session.add(user)
            db.session.commit()

    @user_bp.response(UserSchema, code=200, description="成功获取到用户信息")
    @login_required
    def get(self):
        """获取所有用户信息（仅网站管理员可操作）

        TODO：加分页，加权限认证
        ---
        :return:
        """
        return current_user

    @user_bp.response(code=204, description="账号删除成功")
    @user_bp.arguments(UserCreateArgsSchema)
    @user_bp.doc(responses={"400": {'description': "删除用户需要再次确认密码"}})
    @login_required
    def delete(self, data: dict):
        """删除当前用户（永久注销）

        ---
        :return:
        """
        # 验证密码
        if current_user.check_password(data['password_hash']):
            db.session.remove(current_user)  # 删除用户，相关资料自动级联删除
            db.session.commit()
        else:
            abort(400, message="delete account need to confirm you password!")

    @login_required
    def patch(self):
        """修改当前用户信息

        ---
        :return:
        """

