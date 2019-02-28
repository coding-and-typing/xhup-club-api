# -*- coding: utf-8 -*-
from app import db

"""
QQ 群相关
"""


class QQGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(20), index=True, nullable=False, unique=True)
    group_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return "<QQGroup '{}', Id '{}'>".format(self.group_name, self.group_id)


class QQUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), index=True, nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return "<QQGroup '{}', Id '{}'>".format(self.username, self.user_id)


# QQ 用户 - QQ 群 对应表
class GroupMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    group_id = db.Column(db.Integer, db.ForeignKey('qq_group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('qq_user.id'))

    nick_name = db.Column(db.String(50))

    is_admin = db.Column(db.Boolean, nullable=False)
    is_owner = db.Column(db.Boolean, nullable=False)
