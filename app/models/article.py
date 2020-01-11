# -*- coding: utf-8 -*-
import hashlib
import json
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates

from app import db
from app.utils import text

"""
文章与赛文
"""


class CompArticle(db.Model):
    """赛文库（包括历史赛文，当前赛文和未来的赛文）"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, nullable=False)  # 赛文标题
    producer = db.Column(db.String(128), index=True, nullable=True)  # 赛文制作人

    content_type = db.Column(db.String(64), index=True, nullable=True)  # 散文、单字、政论等
    content = db.Column(db.Text, nullable=False)  # 赛文内容
    length = db.Column(db.Integer, index=True, nullable=False)  # 赛文长度
    hash = db.Column(db.String(128), nullable=False)  # 赛文内容的 hash

    date = db.Column(db.Date, index=True, nullable=False)  # 赛文日期
    start_time = db.Column(db.Time, nullable=False)  # 赛文开始日期（一般 0 点）
    end_time = db.Column(db.Time, nullable=False)  # 赛文结束时间（一般 23:30:00）

    number = db.Column(db.Integer, nullable=False)  # 赛文期数（编号）
    comp_type = db.Column(db.String(128), index=True, nullable=False)  # 比赛类型（日赛、周赛等）
    level = db.Column(db.Integer, nullable=True)  # 赛文难度评级

    sync = db.Column(db.Integer, nullable=False, default=0)  # 0 未同步，1 同步成功，2 同步失败

    # 赛文所属群组（级联）
    # 通过 backref 添加了 group 引用
    group_db_id = db.Column(db.Integer,
                            db.ForeignKey('group.id', ondelete="CASCADE", onupdate="CASCADE"),
                            index=True, nullable=False)

    __table_args__ = (
        # 群内的赛文内容不要重复。
        UniqueConstraint('title', 'hash', 'length', 'group_db_id'),
        # 群内某一种类型的赛事，期数不能出现重复
        UniqueConstraint('number', 'group_db_id', 'comp_type'),
        # 一个群一天只有一篇赛文
        UniqueConstraint('date', 'group_db_id')
    )

    def __init__(self,
                 title,
                 content: str,
                 content_type,

                 producer,

                 date_,
                 start_time,
                 end_time,

                 number,
                 comp_type,
                 group_db_id,
                 hash_=None,
                 level=None):
        self.title = title
        self.content = content
        self.content_type = content_type
        self.length = len(content)

        self.producer = producer

        self.date = date_
        self.start_time = start_time
        self.end_time = end_time

        self.number = number
        self.comp_type = comp_type
        self.group_db_id = group_db_id
        self.level = level

        # 自动生成 hash，使用 sha1 算法（只是用于防碰撞，不需要 sha256）
        if hash_ and isinstance(hash_, str):
            self.hash = hash_
        else:
            self.hash = hashlib.sha1(content.encode("utf-8")).hexdigest()

    @validates("content")
    def validate_content(self):
        special_chars = text.special_chars(self.content)
        if len(special_chars) != 0:
            return False
        else:
            return True

    def __repr__(self):
        return "<Competition Article '{}' - by {}>".format(self.title, self.author)


class Article(db.Model):
    """文章库，可用于制作赛文"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, nullable=False)  # 文章标题
    author = db.Column(db.String(128), index=True, nullable=True)  # 作者

    content_type = db.Column(db.String(64), index=True, nullable=True)  # 散文、单字、政论等
    content = db.Column(db.Text, nullable=False)  # 文章内容，长度一般在 1000 字以内（但是很多数据库算的是字节数）
    hash = db.Column(db.String(128), nullable=False)  # 文章内容的 hash
    length = db.Column(db.Integer, index=True, nullable=False)  # 文章长度

    special_chars = db.Column(db.String(2040), nullable=False)  # 文章包含的特殊字符

    # 文章的上传者，用户只可以对自己上传的文章进行 CURD 操作。（用户注销后，它为 null）
    # 通过 backref 添加了 main_user 引用
    main_user_id = db.Column(db.Integer,
                             db.ForeignKey('main_user.id'),
                             index=True, nullable=True)

    __table_args__ = (UniqueConstraint('title', 'hash', "length"),)

    def __init__(self,
                 title,
                 author,
                 content_type,
                 content: str,
                 main_user_id=None,
                 special_chars=None,
                 hash_=None):
        self.title = title
        self.author = author
        self.content_type = content_type

        # 对文章进行处理
        content = text.process_text_cn(content)
        self.content = content
        self.length = len(content)

        self.main_user_id = main_user_id

        if special_chars is None:
            special_chars = text.special_chars(content)
        self.special_chars = json.dumps(list(special_chars))  # set 不能序列化，得转成 list

        # 自动生成 hash，使用 sha1 算法（只是用于防碰撞，不需要 sha256）
        if hash_ and isinstance(hash_, str):
            self.hash = hash_
        else:
            self.hash = hashlib.sha1(content.encode("utf-8")).hexdigest()

    def __repr__(self):
        return "<Stored Article '{}' - by {}>".format(self.title, self.author)


class CompArticleBox(db.Model):
    """候选赛文盒子，用于赛文混合"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, nullable=False)  # 文章标题

    content_type = db.Column(db.String(64), index=True, nullable=True)  # 散文、单字、政论等
    content = db.Column(db.Text, nullable=False)  # 文章内容，长度一般在 1000 字以内（但是很多数据库算的是字节数）
    hash = db.Column(db.String(128), nullable=False)  # 文章内容的 hash
    length = db.Column(db.Integer, index=True, nullable=False)  # 文章长度
    level = db.Column(db.Integer, nullable=True)  # 赛文难度评级

    # 赛文条目的的所有者（级联删除）
    # 通过 backref 添加了 main_user 引用
    main_user_id = db.Column(db.Integer,
                             db.ForeignKey('main_user.id', ondelete="CASCADE", onupdate="CASCADE"),
                             index=True, nullable=False)
    box_id = db.Column(db.Integer, index=True, nullable=False)  # 条目所属的 box 的 id

    __table_args__ = (UniqueConstraint('hash', "length", "main_user_id"),)

    def __init__(self,
                 title,
                 content_type,
                 content: str,
                 main_user_id,
                 box_id,
                 hash_=None,
                 level=None):
        self.title = title

        self.content_type = content_type
        self.content = content

        self.level = level
        self.length = len(content)

        self.main_user_id = main_user_id
        self.box_id = box_id

        # 自动生成 hash，使用 sha1 算法（只是用于防碰撞，不需要 sha256）
        if hash_ and isinstance(hash_, str):
            self.hash = hash_
        else:
            self.hash = hashlib.sha1(content.encode("utf-8")).hexdigest()


