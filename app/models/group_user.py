# -*- coding: utf-8 -*-
import json

from sqlalchemy import UniqueConstraint

from app import db

"""
其他聊天平台的 账号/群组 数据，目前计划包括：qq、wechat 和 telegram

用户绑定聊天平台的 账号/群组 时，相关数据会保存到这里
"""


class GroupUserRelation(db.Model):
    """
    GroupUser 与 Group 的关联表
    """
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(10), index=True, nullable=False)  # qq、wechat 或 telegram
    group_db_id = db.Column(db.Integer,
                            db.ForeignKey('group.id', ondelete="CASCADE", onupdate="CASCADE"),
                            index=True, nullable=False)
    user_db_id = db.Column(db.Integer,
                           db.ForeignKey('group_user.id', ondelete="CASCADE", onupdate="CASCADE"),
                           index=True, nullable=False)

    is_admin = db.Column(db.Boolean, nullable=False)
    is_owner = db.Column(db.Boolean, nullable=False)

    # 特定平台下，用户 - 群组的映射不应该重复！
    __table_args__ = (UniqueConstraint('platform', 'user_db_id', 'group_db_id', name='c_relation'),)


class Group(db.Model):
    """各群组"""
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(10), index=True, nullable=False)  # qq、wechat 或 telegram
    group_id = db.Column(db.String(20), index=True, nullable=False)  # 群的唯一 id
    group_name = db.Column(db.String(50), nullable=False)  # 群名称

    # 通过 backref，这里动态添加了一个 users 属性

    # 添加拆字表引用（不级联删除）
    char_table = db.relationship("CharTable", backref="group", lazy="dynamic")

    # 赛文引用（级联）
    comp_articles = db.relationship("CompArticle", backref="group", lazy="dynamic",
                                    passive_deletes="cascade")

    # 特定平台下，群的 id 应该是唯一的
    __table_args__ = (UniqueConstraint('platform', 'group_id', name="c_group"),)

    def __repr__(self):
        return "<{} Group '{}', Id '{}'>".format(self.platform, self.group_name, self.group_id)


class GroupUser(db.Model):
    """群组成员"""
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(10), index=True, nullable=False)  # qq、wechat 或 telegram
    user_id = db.Column(db.String(20), index=True, nullable=False)  # 用户的唯一 id
    username = db.Column(db.String(50), nullable=False)

    # 当前用户所绑定到的 main_user（级联）
    # 通过 backref 添加了 main_user 属性
    main_user_id = db.Column(db.Integer,
                             db.ForeignKey('main_user.id', ondelete="CASCADE", onupdate="CASCADE"),
                             index=True, nullable=False)

    # 所属群组（可以有多个）
    groups = db.relationship("Group",
                             secondary=GroupUserRelation.__table__,  # secondary 指定多对多的关联表（中间表）
                             backref="users",  # 在表 group 中添加反向引用键 'user'
                             lazy="dynamic")  # 动态计算表关系

    # 特定平台下，用户的 id 应该是唯一的
    __table_args__ = (UniqueConstraint('platform', 'user_id', name='c_group_user'),)

    def __repr__(self):
        return "<{} Group '{}', Id '{}'>".format(self.platform, self.username, self.user_id)
