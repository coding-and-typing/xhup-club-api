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


"""
这里的文章，可能包括散文、中短篇小说、政论甚至长篇小说（目前没有考虑保存这么长的小说），
用于在 comp_articles 中生成群组赛文。

操作对象可以为复数个。
"""


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

