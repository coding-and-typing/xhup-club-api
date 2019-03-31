# -*- coding: utf-8 -*-
import json
import logging

from flask.views import MethodView
import marshmallow as ma
from flask_login import current_user

from app.utils.captcha import generate_captcha_code
from app.utils.common import login_required, timestamp
from flask_rest_api import abort, Blueprint

from app import api_rest, redis, current_config
from app.api import api_prefix

logger = logging.getLogger(__name__)

relation_bp = Blueprint(
    'relation', __name__, url_prefix=f'{api_prefix}/relation',
    description="用户与群组的绑定（建立 relation）"
)


@api_rest.definition('Relation')
class RelationSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True
    timestamp = ma.fields.String()
    verification_code = ma.fields.String()


@relation_bp.route("/")
class RelationView(MethodView):
    """用户与群组关系的增删查改"""

    decorators = [login_required]

    @relation_bp.response(schema=RelationSchema, code=201,
                          description="""成功生成验证码，三分钟内有效。
                          请将收到的验证码发送到需要绑定的群组中，以完成绑定。（验证消息格式：`拆小鹤验证：xxxxxx`）""")
    def post(self):
        """新建用户与群组的绑定
        """
        # 生成验证码
        verification_code = generate_captcha_code()
        payload = {
            "user_db_id": current_user.id,
            "verification_code": verification_code,
            "timestamp": timestamp(),
        }
        redis.connection.set(str(verification_code),
                             json.dumps(payload),
                             ex=current_config.VERIFICATION_CODE_EXPIRES)
        return payload  # 返回的是临时验证信息

    def delete(self):
        """删除关系"""
        pass

    def get(self):
        """获取已有的关系表"""
        pass

