# -*- coding: utf-8 -*-
import logging

from flask.views import MethodView
import marshmallow as ma
from flask_rest_api import abort, Blueprint

from app import api_rest, current_config
from app.api import api_prefix
from app.service.words import character
from app.utils.common import login_required

logger = logging.getLogger(__name__)

char_bp = Blueprint(
    'char', __name__, url_prefix=f'{api_prefix}/char',
    description="小鹤双拼相关的功能"
)

"""
查询文字编码表（小鹤音形等）
"""


class TableCreateArgsSchema(ma.Schema):
    """请求应该带有的参数

    """
    class Meta:
        strict = True
        ordered = True

    version = ma.fields.String(required=True)
    table = ma.fields.String(required=True)

    table_name = ma.fields.String(required=True)  # 编码表名称（如小鹤音形拆字表）

    group_id = ma.fields.String(required=True)  # 一个编码表，需要绑定一个群号。
    group_platform = ma.fields.String(required=True)  # 该群所属平台


@api_rest.definition('Char')
class CharSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True

    char = ma.fields.String()
    info = ma.fields.String()
    version = ma.fields.String()


@char_bp.route("/chars")
class CharView(MethodView):
    """拆字表查询 api"""

    @char_bp.arguments(TableCreateArgsSchema)
    @char_bp.response(code=201)
    @login_required
    def post(self, data: dict):
        """提交新的拆字表

        1. 拆字表必须要带版号，而且版号必须比之前的高。
        2. 只允许群管理员上传拆字表，上传时需要指定 群id。
        3. 第一次上传后，该拆字表就只允许该群的管理员进行更新了。
        ---
        :return None
        """
        # TODO 验证当前用户是指定群的管理员
        abort(401, message="you are not the admin of this group")

        try:
            character.save_split_table(**data)
        except RuntimeError as e:
            abort(400, message=e.args)

    @char_bp.arguments(CharSchema)
    @char_bp.response(CharSchema, code=200, description="成功获取到 char 的 info")
    def get(self, data: dict):
        """查字，这个是最常用的方法

        默认使用最新的拆字表
        """
        info = character.get_info(**data)
        if not info:
            abort(404, message=f"no info for character {data['char']}")

        return info
