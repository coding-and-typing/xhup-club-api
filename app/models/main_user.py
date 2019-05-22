# -*- coding: utf-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

"""
这个用户，是指系统的主用户，需要绑定邮箱，设置密码

用户其他平台的账号，都是绑定到这个主用户。
"""


class MainUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # 拆五笔账号（仅群管理）
    chaiwubi_user = db.relationship("ChaiWuBiUser",
                                    backref=db.backref("main_user", lazy="dynamic"),
                                    lazy="dynamic",
                                    passive_deletes="cascade")

    # 一个账号，可以绑定多个群组用户
    group_users = db.relationship("GroupUser",
                                  backref=db.backref("main_user", lazy="dynamic"),
                                  lazy="dynamic",
                                  passive_deletes="cascade")

    # 此账号创建的 articles（不级联删除，所以不加 passive_deletes）
    articles = db.relationship("Article",
                               backref=db.backref("main_user", lazy="dynamic"),
                               lazy="dynamic")

    # 此账号创建的候选赛文
    comp_article_boxes = db.relationship("CompArticleBox",
                                         backref=db.backref("main_user", lazy="dynamic"),
                                         lazy="dynamic",
                                         passive_deletes="cascade")

    # 此账号创建的码表
    word_tables = db.relationship("WordTable",
                                  backref=db.backref("main_user", lazy="dynamic"),
                                  lazy="dynamic",
                                  passive_deletes="cascade")

    # 此账号创建的拆字表
    char_table = db.relationship("CharTable",
                                 backref=db.backref("main_user", lazy="dynamic"),
                                 lazy="dynamic",
                                 passive_deletes="cascade")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email

        # 设置密码（hash）
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<Main User {}>'.format(self.username)

    def set_password(self, password: str):
        """只用于修改密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return MainUser.query.get(int(user_id))
