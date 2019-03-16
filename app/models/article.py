# -*- coding: utf-8 -*-

from sqlalchemy import UniqueConstraint

from app import db

"""
文章与赛文
"""


class CompArticle(db.Model):
    """赛文库（包括历史赛文，和未来的赛文）"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, nullable=False)  # 文章标题
    producer = db.Column(db.String(128), index=True, nullable=True)  # 赛文制作人
    type = db.Column(db.String(64), index=True, nullable=True)  # 散文、单字、政论等
    article = db.Column(db.Text, nullable=False)  # 文章内容
    hash = db.Column(db.String(128), nullable=False)  # 文章内容的 hash

    date = db.Column(db.Date, nullable=False)  # 赛文日期
    number = db.Colum(db.Integer, nullable=False)  # 赛文期数（编号）
    comp_type = db.Column(db.String(128), nullable=False)  # 比赛类型（日赛、周赛等）
    level = db.Column(db.Integer, nullable=True)  # 赛文难度评级

    # 赛文所属群组
    group_db_id = db.Column(db.Integer, db.ForeignKey('group.id'), index=True, nullable=False)

    __table_args__ = (UniqueConstraint('title', 'hash', 'group_db_id', name='c_comp_article'),)

    def __repr__(self):
        return "<Competition Article '{}' - by {}>".format(self.title, self.author)


class Article(db.Model):
    """文章库，可用于制作赛文"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, nullable=False)  # 文章标题
    author = db.Column(db.String(128), index=True, nullable=True)  # 作者
    type = db.Column(db.String(64), index=True, nullable=True)  # 散文、单字、政论等
    article = db.Column(db.Text, nullable=False)  # 文章内容
    hash = db.Column(db.String(128), nullable=False)  # 文章内容的 hash
    special_chars = db.Column(db.String(2040))  # 文章包含的特殊字符

    __table_args__ = (UniqueConstraint('title', 'hash', name='c_article'),)

    def __repr__(self):
        return "<Article '{}' - by {}>".format(self.title, self.author)

