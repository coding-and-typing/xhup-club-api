# -*- coding: utf-8 -*-
import json
import logging

from flask.views import MethodView
import marshmallow as ma
from flask_login import current_user

from app.models import GroupUserRelation
from app.utils.captcha import generate_captcha_code
from app.utils.common import login_required, timestamp
from flask_smorest import abort, Blueprint, Page

from app import api_rest, redis, current_config, db
from app.api import api_prefix

logger = logging.getLogger(__name__)

relation_bp = Blueprint(
    'relation', __name__, url_prefix=f'{api_prefix}/relation',
    description="用户与群组的绑定（建立 relation）"
)


class RelationCreateArgsSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True
    timestamp = ma.fields.String()
    verification_code = ma.fields.String()


class RelationSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True

    username = ma.fields.String()
    user_id = ma.fields.String(required=True)

    group_name = ma.fields.String()
    group_id = ma.fields.String(required=True)

    is_admin = ma.fields.Boolean(dump_only=True)
    is_owner = ma.fields.Boolean(dump_only=True)


@relation_bp.route("/")
class RelationView(MethodView):
    """用户与群组关系的增删查改"""

    @relation_bp.response(schema=RelationCreateArgsSchema, code=201,
                          description="成功生成验证码，三分钟内有效。\n"
                                      "请将收到的验证码发送到需要绑定的群组中，以完成绑定。（验证消息格式：`拆小鹤验证：xxxxxx`）")
    @login_required
    def post(self):
        """新建用户与群组的绑定
        """
        # 生成验证码
        verification_code = generate_captcha_code()
        payload = {
            "user_db_id": current_user.id,
            "verification_code": verification_code,
            "timestamp": timestamp(),
            "expires": current_config.VERIFICATION_CODE_EXPIRES
        }

        key = current_config.GROUP_BIND_VERI_FORMAT.format(verification_code)
        redis.connection.set(key,
                             json.dumps(payload),
                             ex=current_config.VERIFICATION_CODE_EXPIRES)
        return payload  # 返回的是临时验证信息

    @relation_bp.response(RelationSchema(many=True), code=200, description="成功获取到数据")
    @relation_bp.paginate(Page)
    @login_required
    def get(self):
        """获取已有的关系表"""
        res = []
        for user in current_user.group_users:
            for relation in user.relations:
                res.append({
                    "username": user.username,  # QQ 昵称
                    "user_id": user.user_id,  # QQ 号码

                    "group_name": relation.group.group_name,
                    "group_id": relation.group.id,

                    "is_admin": relation.is_admin,
                    "is_owner": relation.is_owner,
                })

        return res

    @relation_bp.arguments(RelationSchema)
    @relation_bp.response(code=201, description="删除成功")
    @login_required
    def delete(self, data: dict):
        """删除与某群组的绑定"""
        relations = current_user.group_users \
            .fiter_by(user_id=data['user_id']) \
            .first() \
            .relations

        relations.filter(GroupUserRelation.c.group.group_id == data['group_id']) \
            .delete()
        db.session.commit()

