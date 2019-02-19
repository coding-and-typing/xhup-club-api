# -*- coding: utf-8 -*-
import logging

from flask.views import MethodView
import marshmallow as ma
from flask_rest_api import abort, Blueprint

from app import api_rest
from app.api import api_prefix

logger = logging.getLogger(__name__)

xhup_bp = Blueprint(
    'xhup', __name__, url_prefix=f'{api_prefix}/xhup',
    description="小鹤双拼相关的功能"
)


@xhup_bp.route("/chars")
class CharView(MethodView):
    """小鹤音形 拆字表查询 api"""

    def post(self):
        """提交新的拆字表

        只允许【散步的鹤】，或者网站管理员访问此 api
        必须要带版号，而且版号必须比之前的高。
        """
        pass

    def get(self):
        """查字，这个是最常用的方法
        默认使用最新的拆字表
        """
        pass

