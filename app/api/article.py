# -*- coding: utf-8 -*-
import logging

from flask.views import MethodView
import marshmallow as ma
from app.utils.common import login_required

from app.api import article_bp

logger = logging.getLogger(__name__)


"""
这里的文章，可能包括散文、中短篇小说、政论甚至长篇小说（目前没有考虑保存这么长的小说），
用于在 comp_article 中生成群组赛文。

操作对象可以为复数个。
"""


@article_bp.route("/")
class ArticleView(MethodView):
    """文章的增删查改"""

    # flask_smorest 不能通過這個參數生成對應的 openapi 文檔。
    # decorators = [login_required]

    @login_required
    def post(self):
        """增加文章

        可选：随机一文、从文档添加
        """
        pass

    @login_required
    def delete(self):
        """删除文章"""
        pass

    @login_required
    def get(self):
        """获取文章列表"""
        pass

    @login_required
    def patch(self):
        """修改文章

        ---
        :return:
        """
        pass

