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
    """赛文库（包括历史赛文，和未来的赛文）"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, nullable=False)  # 文章标题
    producer = db.Column(db.String(128), index=True, nullable=True)  # 赛文制作人
    content_type = db.Column(db.String(64), index=True, nullable=True)  # 散文、单字、政论等

    # TODO content 可能为长篇小说。暂时没有考虑这种情况
    content = db.Column(db.Text, nullable=False)  # 文章内容
    hash = db.Column(db.String(128), nullable=False)  # 文章内容的 hash

    date = db.Column(db.Date, nullable=False)  # 赛文日期
    number = db.Colum(db.Integer, nullable=False)  # 赛文期数（编号）
    comp_type = db.Column(db.String(128), nullable=False)  # 比赛类型（日赛、周赛等）
    level = db.Column(db.Integer, nullable=True)  # 赛文难度评级

    # 赛文所属群组
    group_db_id = db.Column(db.Integer, db.ForeignKey('group.id'), index=True, nullable=False)

    __table_args__ = (UniqueConstraint('title', 'hash', 'group_db_id', name='c_comp_article'),)

    def __init__(self,
                 title,
                 producer,
                 content_type,
                 content: str,
                 date,
                 number,
                 comp_type,
                 group_db_id,
                 level=None):
        self.title = title
        self.producer = producer
        self.content_type = content_type
        self.content = content
        self.date = date
        self.number = number
        self.comp_type = comp_type
        self.group_db_id = group_db_id
        self.level = level

        # 自动生成 hash，使用 sha1 算法（只是用于防碰撞，不需要 sha256）
        self.hash = hashlib.sha1(content.encode("utf-8"))

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
    special_chars = db.Column(db.String(2040), nullable=False)  # 文章包含的特殊字符

    __table_args__ = (UniqueConstraint('title', 'hash', name='c_article'),)

    def __init__(self,
                 title,
                 author,
                 content_type,
                 content: str):
        self.title = title
        self.author = author
        self.content_type = content_type

        # 对文章进行处理
        content = text.process_text_cn(content)
        self.content = content

        special_chars = text.special_chars(content)
        self.special_chars = json.dumps(list(special_chars))  # set 不能序列化，得转成 list

        # 自动生成 hash，使用 sha1 算法（只是用于防碰撞，不需要 sha256）
        self.hash = hashlib.sha1(content.encode("utf-8"))

    def __repr__(self):
        return "<Stored Article '{}' - by {}>".format(self.title, self.author)

