# -*- coding: utf-8 -*-
import datetime
import logging
from typing import Dict

from flask.views import MethodView
import marshmallow as ma
from flask_login import current_user
from flask_rest_api import abort, Blueprint, Page
from marshmallow import validates, ValidationError

from app import api_rest, db
from app.api import api_prefix
from app.models import CompArticleBox
from app.service.articles.article_ import add_comp_article_box, delete_comp_article_box, add_comp_articles_from_box
from app.utils.common import login_required

logger = logging.getLogger(__name__)

comp_article_bp = Blueprint(
    'comp_article', __name__, url_prefix=f'{api_prefix}/comp_article',
    description="（各群组）赛文的增删查改"
)


"""
即所有历史赛文与未来的赛文。
要批量添加赛文，首先要把赛文批量添加到赛文 box 里，
然后在 post comp_articles/ 时指定赛文来源为 'box'。

操作对象有复数个。
"""


class CompArticleBoxCreateArgsSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True

    content_type = ma.fields.String(required=True)  # 随机散文、乱序单字、从文档添加
    length = ma.fields.Integer(required=True)  # 赛文长度，建议 300-800 之间，乱序单字 30 - 70 之间
    delta = ma.fields.Integer(default=30)  # 赛文长度的允许误差，默认 30
    count = ma.fields.Integer(required=True)  # 添加的赛文篇数，不得超过这个数额。最多 999 篇

    # 从文档添加赛文时，此参数为赛文文本的类型：散文、政论、小说等
    # 添加乱序单字时，此参数为前五百“top_500”、中五百“middle_500”、后五百“last_500”或者前一千五“top_1500”
    content_type_2 = ma.fields.String()

    # 如果是从文档添加，下列参数可用
    title = ma.fields.String()  # 赛文标题
    text = ma.fields.String()  # 文档的内容，str
    separator = ma.fields.String()  # 如果指定了这个，就忽略掉 length

    __content_type_options = [  # content_type 的可选项
        "random_article",  # 随机散文
        "shuffle_chars",  # 乱序单字
        "given_text",  # 从文档添加
    ]

    @validates("content_type")
    def validate_version(self, content_type: str):
        if content_type not in self.__content_type_options:
            raise ValidationError(f"invalid content_type, not in {self.__content_type_options}")


class CompArticleBoxArgsSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True

    count = ma.fields.Integer(dump_only=True)  # 所含赛文的篇数
    content_type = ma.fields.String(dump_only=True)  # 随机散文、乱序单字、混合赛文等

    # 以下参数用于 get delete patch
    box_id = ma.fields.Integer(required=True)  # 赛文盒 id
    id = ma.fields.Integer()  # 候选赛文的 id

    # 以下参数用于 get patch
    title = ma.fields.String()  # 赛文标题
    content = ma.fields.String()  # 文档的内容，str
    length = ma.fields.Integer()  # 赛文长度，建议 300-800 之间，乱序单字 30 - 70 之间


class CompArticleCreateArgsSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True

    platform = ma.fields.String(required=True)
    group_id = ma.fields.String(required=True)  # 要求当前用户为指定群组的管理员

    comp_type = ma.fields.String(required=True)  # 赛事类型（周赛日赛等）

    start_number = ma.fields.String(required=True)  # 赛文起始期数
    start_date = ma.fields.Date(default=None)  # 赛文起始日期，默认为已有赛文的最后一天+1
    start_time = ma.fields.Time(default=datetime.time(0, 0, 0, 0))  # 赛文起始时间(默认为 00:00:00)
    end_time = ma.fields.Time(default=datetime.time(23, 30, 0, 0))   # 赛文结束时间（默认为 23:30:00）

    mix_mode = ma.fields.String(required=True)  # random / top2down / proportionally
    en = ma.fields.Boolean()  # 内容为英文，使用英文的处理函数。
    scale_list = ma.fields.Dict()  # 分配比例，仅 mode 为 proportionally 时可用。[ 3, 2, 1]


class CompArticleQueryArgsSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True

    platform = ma.fields.String(required=True)
    group_id = ma.fields.String(required=True)  # 要求当前用户为指定群组的管理员

    comp_type = ma.fields.String()  # 赛事类型（周赛日赛等）

    start_number = ma.fields.Integer()  # 赛文起始期数
    end_number = ma.fields.Integer()

    start_date = ma.fields.Date()  # 赛文起始日期，默认为已有赛文的最后一天+1
    end_date = ma.fields.Date()


@comp_article_bp.route("/box")
class CompArticleBoxView(MethodView):
    """赛文 box 的增删查改
        将赛文分成不同的 box，这样在提交赛文时，就可以指定赛文的混合方式。（通过 post comp_articles/）
    """

    decorators = [login_required]

    @comp_article_bp.arguments(CompArticleBoxCreateArgsSchema)
    @comp_article_bp.response(code=201, description="赛文盒添加成功")
    def post(self, data: Dict):
        """添加一个赛文 box
        """
        code, res = add_comp_article_box(data, current_user)
        if code == 200:
            return res
        else:
            abort(code, description=res)

    @comp_article_bp.arguments(CompArticleBoxArgsSchema)
    @comp_article_bp.response(code=204, description="赛文盒删除成功")
    def delete(self, data: dict):
        """删除赛文 box"""
        delete_comp_article_box(data, current_user)

    @comp_article_bp.arguments(CompArticleBoxArgsSchema)
    @comp_article_bp.response(CompArticleBoxArgsSchema(many=True), code=200, description="成功获取到数据")
    @comp_article_bp.paginate(Page)  # 分页
    def get(self, data: dict):
        """获取赛文 box，分页"""
        return db.session.query(CompArticleBox) \
            .filter_by(**data, main_user_id=current_user.id) \
            .order_by(CompArticleBox.id).all()


@comp_article_bp.route("/")
class CompArticleView(MethodView):
    """赛文的增删查改，要求用户有群管理权限"""

    decorators = [login_required]

    @comp_article_bp.arguments(CompArticleCreateArgsSchema)
    @comp_article_bp.response(code=201, description="赛文添加成功")
    def post(self, data: dict):
        """将所有候选赛文盒的内容添加为赛文
        """
        code, res = add_comp_articles_from_box(data, current_user)
        if code == 200:
            return res
        else:
            abort(code, description=res)

    def delete(self):
        """删除赛文"""
        pass


    def get(self, data):
        """获取赛文"""
        pass

    def patch(self):
        """修改赛文

        ---
        :return:
        """
        pass

