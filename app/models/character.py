# -*- coding: utf-8 -*-
from sqlalchemy import UniqueConstraint

from app import db


"""
通用的文字编码表
"""


class CharTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), unique=True, nullable=False)

    # 所属的拆字表版本号，应使用 pkg_resources.parse_version 做比较
    version = db.Column(db.String(20), index=True, nullable=False)

    description = db.Column(db.String(2048))  # 描述，比如新版本更新了啥。

    # 拆字表所属群组，群管理员可编辑该表。（其他群只能选用该表，不能修改）
    # 通过 backref 添加了 group 引用
    group_db_id = db.Column(db.Integer,
                            db.ForeignKey('group.id'),
                            index=True, nullable=True)

    # 拆字表的创建者（级联删除）
    main_user_id = db.Column(db.Integer,
                             db.ForeignKey('main_user.id', ondelete="CASCADE", onupdate="CASCADE"),
                             index=True, nullable=False)

    # 单字列表（级联删除）
    characters = db.relationship("Character",
                                 backref="table",
                                 lazy="dynamic",
                                 passive_deletes="cascade")

    # 同一张拆字表的同一个版本号只能使用一次
    __table_args__ = (UniqueConstraint('name', 'version', name="c_chars_table"),)

    def __repr__(self):
        return "<Chars Table '{}'>".format(self.name)


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    char = db.Column(db.String(6), index=True, nullable=False)  # utf-8 最长 6 字节
    codes = db.Column(db.String(64), nullable=False)  # 可用编码，用空格分隔
    split = db.Column(db.String(200))  # 单字的拆分
    other_info = db.Column(db.String(200))  # 其他拆分信息，对小鹤音形来说，这是"首末编码"信息

    # 所属的拆字表 id
    # 通过 backref 添加了 table
    table_db_id = db.Column(db.Integer,
                            db.ForeignKey('char_table.id', ondelete="CASCADE", onupdate="CASCADE"),
                            index=True, nullable=False)

    # 同一张拆字表中，同一个单字只应该有一个词条
    __table_args__ = (UniqueConstraint('table_db_id', 'char', name='c_char'),)

    def __repr__(self):
        return "<Char '{}'>".format(self.char)


