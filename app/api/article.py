# -*- coding: utf-8 -*-
import logging

from flask.views import MethodView
import marshmallow as ma
from app.utils.common import login_required
from flask_rest_api import abort, Blueprint

from app import api_rest
from app.api import api_prefix

logger = logging.getLogger(__name__)

article_bp = Blueprint(
    'article', __name__, url_prefix=f'{api_prefix}/article',
    description="文章库的增删查改（待实现）"
)


"""
这里的文章，可能包括散文、中短篇小说、政论甚至长篇小说（目前没有考虑保存这么长的小说），
用于在 comp_article 中生成群组赛文。

操作对象可以为复数个。
"""


@article_bp.route("/")
class ArticleView(MethodView):
    """文章的增删查改"""

    decorators = [login_required]

    def post(self):
        """增加文章

        可选：随机一文、从文档添加
        """
        pass

    def delete(self):
        """删除文章"""
        pass

    def get(self):
        """获取文章列表"""
        pass

    def patch(self):
        """修改文章

        ---
        :return:
        """
        pass

