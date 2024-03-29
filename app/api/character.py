# -*- coding: utf-8 -*-
import json
import logging

from flask.views import MethodView
import marshmallow as ma
from flask_login import current_user
from flask_smorest import abort
from marshmallow import validates, ValidationError
from pkg_resources import parse_version

from app.api import table_bp
from app.service.words import character
from app.utils.common import login_required
from app.utils.db import get_group

logger = logging.getLogger(__name__)


"""
拆字表（小鹤音形等，即文字编码的详细）

每次只能操作一个群组的拆字表，所以用单数。
"""


class TableSchema(ma.Schema):
    """请求应该带有的参数

    """
    class Meta:
        strict = True
        ordered = True

    version = ma.fields.String(required=True)
    table = ma.fields.String(required=True, load_only=True)
    table_type = ma.fields.String(required=True)

    table_name = ma.fields.String(required=True)  # 编码表名称（如小鹤音形拆字表）

    description = ma.fields.String()

    group_id = ma.fields.String(required=True)  # 一个编码表，需要绑定一个群号。
    platform = ma.fields.String(required=True)  # 该群所属平台

    @validates("version")
    def validate_version(self, version: str):
        try:
            parse_version(version)
        except RuntimeError as e:
            raise ValidationError("invalid version")

    @validates("table")
    def validate_table(self, table: str):
        if len(table) > 400000:
            raise ValidationError("table is too large")


@table_bp.route("/table/")
class TableView(MethodView):
    """拆字表增添刪查改 api"""

    @table_bp.arguments(TableSchema)
    @table_bp.response(TableSchema, code=201, description="拆字表创建成功")
    @table_bp.doc(responses={"403": {'description': "仅与该拆字表绑定的群的管理员可更新此表"}})
    @table_bp.doc(responses={"409": {'description': "提交的拆字表已经存在"}})
    @login_required
    def post(self, data: dict):
        """提交新的拆字表

        1. 拆字表必须要带版号，而且版号必须比之前的高。
        2. 只允许群管理员上传拆字表，上传时需要指定 群id。
        3. 第一次上传后，该拆字表就只允许该群的管理员进行更新了。
        ---
        :return None
        """
        # 验证当前用户是指定群的管理员
        if get_group(group_id=data['group_id'], platform=data['platform']) \
                not in current_user.auth_groups:
            abort(403, message="you are not the admin of this group")

        success, res = character.save_char_table(**data, main_user=current_user)
        if not success:  # 拆字表已经存在
            # 详见 https://www.stackoverflow.com/questions/3825990
            abort(409, message=res['message'])

        return res


class CharInfoSchema(ma.Schema):
    char = ma.fields.String()
    codes = ma.fields.String()
    split = ma.fields.String()
    other_info = ma.fields.Dict()


class CharSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True

    char = ma.fields.String(required=True)
    info = ma.fields.Nested(CharInfoSchema, dump_only=True)
    version = ma.fields.String()
    table_name = ma.fields.String(required=True)

    @validates("char")
    def validate_table(self, table: str):
        if len(table) != 1:
            raise ValidationError("`char` must be just one character!")


@table_bp.route("/info/")
class CharView(MethodView):
    """拆字表查询 api"""

    @table_bp.arguments(CharSchema, location='query')
    @table_bp.response(CharSchema, code=200, description="成功获取到 char 的 info")
    @table_bp.doc(responses={"404": {'description': "拆字表中不包含该单字的信息"}})
    def get(self, data: dict):
        """查字，这个是最常用的方法

        默认使用最新的拆字表
        """
        info = character.get_info(**data)
        if not info:
            abort(404, message=f"no info for character {data['char']}")

        data['info'] = info
        return data
