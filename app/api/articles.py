# -*- coding: utf-8 -*-
import logging

from flask.views import MethodView
import marshmallow as ma
from app.utils.common import login_required
from flask_rest_api import abort, Blueprint

from app import api_rest
from app.api import api_prefix

logger = logging.getLogger(__name__)

articles_bp = Blueprint(
    'articles', __name__, url_prefix=f'{api_prefix}/articles',
    description="文章库的增删查改"
)


@articles_bp.route("/")
class CompArticlesView(MethodView):
    """赛文的增删查改"""

    decorators = [login_required]

    def post(self):
        """增加赛文

        可选：随机赛文、乱序单字、从文档添加
        """
        pass

    def delete(self):
        """删除赛文"""
        pass

    def get(self):
        """获取赛文"""
        pass

    def patch(self):
        """修改赛文

        ---
        :return:
        """
        pass

