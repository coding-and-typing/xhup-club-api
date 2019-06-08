# -*- coding: utf-8 -*-
import json
import logging
import typing

from flask.views import MethodView
from flask_login import current_user
import marshmallow as ma
from flask_rest_api import abort, Blueprint
from sqlalchemy.exc import IntegrityError

from app import api_rest, db, current_config, redis
from app.models import MainUser
from app.utils.captcha import generate_captcha_code
from app.utils.common import login_required, timestamp
from app.api import api_prefix

logger = logging.getLogger(__name__)

user_bp = Blueprint(
    'user', __name__, url_prefix=f'{api_prefix}/user',
    description="用户的注册、用户信息的获取与修改"
)

"""
用户只能对自己的信息做 CURD，因此用单数。
"""


@api_rest.schema('User')
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
    password = ma.fields.String(required=True, load_only=True)


class UserDeleteArgsSchema(ma.Schema):
    """删除用户

    """
    class Meta:
        strict = True
        ordered = True

    password = ma.fields.String(required=True, load_only=True)

class UserPatchArgsSchema(ma.Schema):
    """修改用户信息需要的参数

    """
    class Meta:
        strict = True
        ordered = True

    username = ma.fields.String()
    email = ma.fields.Email()


@user_bp.route('/')
class UserView(MethodView):
    """注册与注销

    即用户的创建与删除
    """

    @user_bp.arguments(UserCreateArgsSchema)
    @user_bp.response(UserSchema, code=201, description="新用户注册成功")
    @user_bp.doc(responses={"403": {'description': "当前已有用户登录，需要先退出登录"}})
    @user_bp.doc(responses={"409": {'description': "用户名或 email 已被使用"}})
    def post(self, data: typing.Dict):
        """用户注册

        ---
        :param data:
        :return:
        """
        if current_user.is_authenticated:
            abort(403, message="please logout first.")

        user = MainUser(username=data['username'],
                        email=data['email'],
                        password=data['password'])

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            abort(409, message="the username or email has been used.")

        return user

    @user_bp.response(UserSchema, code=200, description="成功获取到用户信息")
    @login_required
    def get(self):
        """获取当前用户信息
        ---
        :return:
        """
        return current_user

    @user_bp.response(code=204, description="账号删除成功")
    @user_bp.arguments(UserDeleteArgsSchema)
    @user_bp.doc(responses={"400": {'description': "删除用户需要再次确认密码"}})
    @login_required
    def delete(self, data: dict):
        """删除当前用户（永久注销）

        ---
        :return:
        """
        # 验证密码
        if current_user.check_password(data['password']):
            db.session.delete(current_user)  # 删除用户，相关资料自动级联删除
            db.session.commit()
        else:
            abort(400, message="wrong password")

    @user_bp.arguments(UserPatchArgsSchema)
    @user_bp.response(UserSchema, code=200, description="修改成功")
    @login_required
    def patch(self, data: dict):
        """修改当前用户信息（不包含修改密码）

        ---
        :return:
        """
        for key, value in data.items():
            current_user.__setattr__(key, value)

        db.session.commit()
        return current_user

#
# @user_bp.route('/password')
# class UserPasswordView(MethodView):
#     """修改用户密码
#     有两种方法：
#         1. 直接通过拆小鹤进行账户密码修改，发送「修改密码」给拆小鹤就行
#         2. 通过邮箱验证，将验证消息通过 jwt 编码进链接中，通过该链接修改密码。
#     """
#     def get(self):
#         """使用 jwt 生成密码重置用的编码串，拼成链接发送给用户绑定的邮箱"""
#         verification_code = generate_captcha_code()
#         payload = {
#             "user_db_id": current_user.id,
#             "verification_code": verification_code,
#             "timestamp": timestamp(),
#             "expires": current_config.VERIFICATION_CODE_EXPIRES
#         }
#
#         key = current_config.RESET_PASSWORD_VERI_FORMAT.format(verification_code)
#         redis.connection.set(key,
#                              json.dumps(payload),
#                              ex=current_config.VERIFICATION_CODE_EXPIRES)
#         return payload  # 返回的是临时验证信息
#
#     def patch(self):
#         """通过邮箱跳转进密码修改页面。
#         """


