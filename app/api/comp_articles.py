# -*- coding: utf-8 -*-
import logging
from typing import Dict

from flask.views import MethodView
import marshmallow as ma
from flask_rest_api import abort, Blueprint

from app import api_rest
from app.api import api_prefix
from app.utils.common import login_required

logger = logging.getLogger(__name__)

comp_articles_bp = Blueprint(
    'comp_articles', __name__, url_prefix=f'{api_prefix}/comp_articles',
    description="（各群组）赛文的增删查改"
)


"""
即所有历史赛文与未来的赛文。
要批量添加赛文，首先要把赛文批量添加到赛文 box 里，
然后在 post comp_articles/ 时指定赛文来源为 'box'。

操作对象有复数个。
"""


class ArticlesCreateArgsSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True

    id = ma.fields.String(dump_only=True)  # 数据库的主键

    use_boxes = ma.fields.Boolean(required=True)  # 是否从 boxes 添加赛文
    platform = ma.fields.String(required=True)
    group_id = ma.fields.String(required=True)  # 要求当前用户为指定群组的管理员

    start_number = ma.fields.String(required=True)  # 赛文起始期数
    start_date = ma.fields.Date(required=True)  # 赛文起始日期
    start_time = ma.fields.Time(required=True)  # 赛文起始时间(默认为 00:00:00)
    end_time = ma.fields.Time(required=True)   # 赛文结束时间（默认为 23:30:00）
    sub_type = ma.fields.String(required=True)  # 赛事类型（周赛日赛等）

    # use_boxes 为 true 时，下列参数可用
    mode = ma.fields.String()  # random / top2down / proportionally
    scale_list = ma.fields.Dict()  # 分配比例，仅 mode 为 proportionally 时可用。{id1: scale, id2: scale, id3:scale}


class ArticlesBoxCreateArgsSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True

    id = ma.fields.String(dump_only=True)  # 数据库的主键

    content_type = ma.fields.String(required=True)  # 随机赛文、乱序单字、从文档添加
    length = ma.fields.Integer(required=True)  # 赛文长度，建议 300-800 之间，乱序单字 30 - 70 之间
    count = ma.fields.Integer(required=True)  # 添加的赛文篇数，不得超过这个数额。
    # 如果是从文档添加，下列参数可用
    title = ma.fields.String()  # 赛文标题
    content_type_2 = ma.fields.String()  # 赛文文本的类型


@comp_articles_bp.route("/boxes")
class CompArticlesBoxView(MethodView):
    """赛文 box 的增删查改
        将赛文分成不同的 box，这样在提交赛文时，就可以指定赛文的混合方式。（通过 post comp_articles/）
    """

    decorators = [login_required]

    @comp_articles_bp.arguments(ArticlesBoxCreateArgsSchema)
    def post(self, data: Dict):
        """添加一个赛文 box
        """
        pass

    def delete(self):
        """删除赛文 box"""
        pass

    def get(self):
        """获取赛文 box"""
        pass

    def patch(self):
        """修改某一个赛文 box"""
        pass


@comp_articles_bp.route("/")
class CompArticlesView(MethodView):
    """赛文的增删查改，要求用户有群管理权限"""

    decorators = [login_required]

    def post(self):
        """添加赛文到赛文列表，有两种方式：
            2. 赛文起始期数、赛文起始日期
            3. 赛文开始时间、赛文结束时间（一般是 00:00:00 到 23:30:00）
            4. 赛事类型（日赛周赛等）

        赛文制作者名称就使用用户的用户名，不可更改。
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

