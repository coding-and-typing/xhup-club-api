# -*- coding: utf-8 -*-

from sqlalchemy import UniqueConstraint

from app import db

"""
码表，或者说词库
"""


class WordsTable(db.Model):
    """码表"""
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), index=True, unique=True, nullable=False)

    # 所属的码表版本号，应使用 pkg_resources.parse_version 做比较
    version = db.Column(db.String(20), index=True, nullable=False)

    # 码表所属群组，该群管理员可编辑该表（不级联，允许 null）
    group_db_id = db.Column(db.Integer,
                            db.ForeignKey('group.id'),
                            index=True, nullable=True)

    # 码表的创建者（级联删除）
    main_user_id = db.Column(db.Integer,
                             db.ForeignKey('main_user.id', ondelete="CASCADE", onupdate="CASCADE"),
                             index=True, nullable=False)

    # 码表中的所有条目
    words = db.relationship("Word",
                            backref="table",
                            lazy="dynamic",
                            passive_deletes="cascade")

    # 同一张码表的同一个版本号只能使用一次
    __table_args__ = (UniqueConstraint('name', 'version', name='c_word_table'),)

    def __repr__(self):
        return "<Word Table '{}'>".format(self.name)


class Word(db.Model):
    """码表中的词条"""
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(6), index=True, nullable=False)  # utf-8 最长 6 字节
    position = db.Column(db.Integer, nullable=False)  # 编码位置：首选1/次选2/三选3
    code = db.Column(db.String(12), nullable=False)  # 词的编码

    # 所属的码表 id
    table_db_id = db.Column(db.Integer,
                            db.ForeignKey('word_table.id', ondelete="CASCADE", onupdate="CASCADE"),
                            index=True, nullable=False)

    # 同一张码表中，一个编码的同一个位置，只能有一个词。
    __table_args__ = (UniqueConstraint('table_db_id', 'code', 'position', name="c_word"),)

    def __repr__(self):
        return "<Word '{}'>".format(self.char)
