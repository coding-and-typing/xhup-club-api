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

