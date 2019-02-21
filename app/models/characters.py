# -*- coding: utf-8 -*-
from app import db


"""
小鹤音形拆字表
"""


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    char = db.Column(db.String, index=True, nullable=False)
    info = db.Column(db.String, nullable=False)

    # 所属的拆字表版本号，应使用 pkg_resources.parse_version 做比较
    # 或者使用支持 Version 字符串的数据库？
    version = db.Column(db.String, index=True, nullable=False)

    def __repr__(self):
        return "<Char '{}'>".format(self.char)


