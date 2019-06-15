# -*- coding: utf-8 -*-
import datetime
import logging
from typing import Dict

from flask.views import MethodView
import marshmallow as ma
from flask_login import current_user
from flask_rest_api import abort, Blueprint, Page
from flask_rest_api.pagination import PaginationParameters
from flask_sqlalchemy import BaseQuery
from marshmallow import validates, ValidationError
from sqlalchemy import desc, asc

from app import api_rest, db
from app.api import api_prefix
from app.models import CompArticleBox, CompArticle, MainUser, ChaiWuBiUser, get_group
from app.service.articles.article_ import add_comp_article_box, delete_comp_article_box, add_comp_articles_from_box
from app.service.articles.chaiwubi import ArticleAdder
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
    delta = ma.fields.Integer()  # 赛文长度的允许误差，默认 30(default 只被用于 dump，没有被用于 load)
    count = ma.fields.Integer(required=True)  # 添加的赛文篇数，不得超过这个数额。最多 999 篇

    # 从文档添加赛文时，此参数为赛文文本的类型：散文、政论、小说等
    # 添加乱序单字时，此参数为前五百“top_500”、中五百“middle_500”、后五百“last_500”或者前一千五“top_1500”
    content_subtype = ma.fields.String()

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

    mode = ma.fields.String()  # 历史文章（past）/未开始赛文（future）

    comp_type = ma.fields.String()  # 赛事类型（周赛日赛等）

    # 查询的起点，只查询此日期之前的赛文（历史），或者这之后的赛文（未来）
    date = ma.fields.Date()  # 赛文日期（默认使用当天日期）


class GroupSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True

    id = ma.fields.Integer()
    platform = ma.fields.String(required=True)  # qq、wechat 或 telegram
    group_id = ma.fields.String(required=True)  # 群的唯一 id
    group_name = ma.fields.String()  # 群名称


@api_rest.definition("CompArticle")
class CompArticleSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True

    id = ma.fields.Integer(required=True)  # delete/patch 方法的参数里必须有 id

    title = ma.fields.String()  # 赛文标题
    producer = ma.fields.String()  # 赛文制作人

    content_type = ma.fields.String()  # 散文、单字、政论等
    content = ma.fields.String()  # 赛文内容
    length = ma.fields.Integer()  # 赛文长度
    hash = ma.fields.String()  # 赛文内容的 hash

    date = ma.fields.Date()  # 赛文日期
    start_time = ma.fields.Time()  # 赛文开始日期（一般 0 点）
    end_time = ma.fields.Time()  # 赛文结束时间（一般 23:30:00）

    number = ma.fields.Integer()  # 赛文期数（编号）
    comp_type = ma.fields.String()  # 比赛类型（日赛、周赛等）
    level = ma.fields.Integer()  # 赛文难度评级

    group = ma.fields.Nested(GroupSchema, dump_only=True)  # 赛文所属群组，不允许修改


class SQLAlchemyPage(Page):
    """分页时，使用 SQLAlchemy 的 Query 类进行分页，
    提升性能。"""
    def __init__(self, collection: BaseQuery, page_params: PaginationParameters):
        """Create a Page instance

        :param sequence collection: base_query
        :page PaginationParameters page_params: Pagination parameters
        """
        # 使用 flask_sqlalchemy 提供的 分页函数进行分页
        self.pagination = collection.paginate(page=page_params.page,
                                              per_page=page_params.page_size)

        super().__init__(collection, page_params)


    @property
    def items(self):
        return self.pagination.items

    @property
    def item_count(self):
        return self.pagination.total


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
        if code == 201:
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

    @comp_article_bp.arguments(CompArticleQueryArgsSchema)
    @comp_article_bp.response(CompArticleSchema(many=True), code=200, description="成功获取到数据")
    @comp_article_bp.paginate(SQLAlchemyPage)
    def get(self, data):
        """获取赛文"""
        articles_query: BaseQuery = db.session.qeury(CompArticle) \
            .filter_by(platform=data["platform"]) \
            .join(CompArticle.group, aliased=True) \
            .filter(group_id=data['group_id'])

        if "comp_type" in data:
            articles_query = articles_query.filter_by(comp_type=data['comp_type'])

        mode = data['mode']
        date = data.get("date",  # 默认使用当前日期
                        datetime.datetime.now().date())
        if mode == "past":  # 查看历史赛文
            articles_query = articles_query.filter(CompArticle.date <= date)\
                .order_by(desc(CompArticle.date))
        elif mode == "future":  # 未开始的赛文
            articles_query = articles_query.filter(CompArticle.date >= date) \
                .order_by(asc(CompArticle.date))
        else:
            abort(400, message="'mode' must be 'past' or 'future'!")

        return articles_query

    @comp_article_bp.arguments(CompArticleSchema)
    @comp_article_bp.response(code=201, description="删除成功")
    def delete(self, data):
        """删除赛文"""
        article: CompArticle = db.session.qeury(CompArticle) \
            .filter_by(id=data.pop('id')).first()

        if not article:
            abort(400, message="the id you specified not exist!")

        if article.group not in current_user.auth_groups:
            abort(401, message="you don't have the authority to modify this article!")

        db.session.delete(article)
        db.session.commit()

    @comp_article_bp.arguments(CompArticleSchema)
    @comp_article_bp.response(CompArticleSchema, code=200, description="修改成功，返回最新内容")
    def patch(self, data: dict):
        """修改赛文

        ---
        :return:
        """
        article: CompArticle = db.session.qeury(CompArticle) \
            .filter_by(id=data.pop('id')).first()

        if not article:
            abort(400, message="the id you specified not exist!")

        if article.group not in current_user.auth_groups:
            abort(401, message="you don't have the authority to modify this article!")

        for key, value in data.items():
            article.__setattr__(key, value)  # 修改赛文

        db.session.commit()  # 最后提交


@comp_article_bp.route("/chaiwubi")
class ChaiWuBiView(MethodView):
    """将指定群组的赛文同步到拆五笔赛文系统（会先清空拆五笔赛文库）
    """

    decorators = [login_required]

    @comp_article_bp.arguments(GroupSchema)
    @comp_article_bp.response(code=201, description="同步成功")
    def post(self, data: Dict):
        c_user: ChaiWuBiUser = current_user.chaiwubi_user
        c_adder = ArticleAdder(c_user.username, c_user.password)

        c_adder.login()  # 登录
        c_adder.delete_all_articles()  # 清空

        # 将所有赛文添加至拆五笔赛文系统
        group = get_group(data['group_id'], data['platform'])
        if group not in current_user.auth_groups:
            abort(401, message="you don't have the authority of this group!")

        failure_count = 0
        for article in group.comp_articles:
            success = c_adder.add_article(
                content=article.content,
                content_type=article.content_type,
                date_=article.date,
                start_time=article.start_time,
                end_time=article.end_time,
                group_id=article.group.id,
                number=article.number,
                title=article.title,
                comp_type=article.comp_type,
                producer=article.producer,
                level=article.level,
            )

            if success:
                article.sync = 1 # 1 表示同步成功
            else:
                article.sync = 2 # 2 表示同步失败
                failure_count += 1
        db.session.commit()  # 提交对 sync 字段的修改
        return {
            "group_id": group.id,
            "total": group.comp_articles.count(),
            "failure_count": failure_count,
        }



