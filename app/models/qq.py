# -*- coding: utf-8 -*-
from app import db


"""
QQ 群相关
"""


class QQGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String, index=True, nullable=False, unique=True)
    group_name = db.Column(db.String, nullable=False)


class QQUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, index=True, nullable=False, unique=True)
    user_name = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    is_owner = db.Column(db.Boolean, nullable=False)


# QQ 用户 - QQ 群 对应表
group_user = db.Table()
