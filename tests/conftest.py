# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import os
from pathlib import Path

import pytest
from flask import Response, url_for

from app import create_app
from app import db as _db
from app.models import Group, GroupUser, GroupUserRelation, MainUser
from config import current_config


@pytest.fixture
def app():
    """An application for the tests."""
    _app = create_app(current_config)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def client(app):
    """A flask test_client"""
    return app.test_client()


@pytest.fixture
def db(app):
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


username = 'ryan'
email = "ryan@example.com"
password = "ihaveadream"


@pytest.fixture
def user(db):
    """A user for the tests."""
    user = MainUser(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return db.session.query(MainUser) \
        .filter_by(username=username, email=email).first()


platform = 'qq'
group_id = '12354321'
user_id = "1233231"

test_text = open(Path(__file__).parent / "resources/青铜葵花.txt",
                 mode='r', encoding="utf-8").read()


@pytest.fixture
def group_admin(db, user):
    """使 user 成为测试群的群管理"""
    group = Group(platform=platform, group_id=group_id, group_name="测试群")
    group_user = GroupUser(platform=platform, user_id=user_id, username="测试管理员", main_user_id=user.id)
    db.session.add_all([group, group_user])

    # 需要获取自动生成的 id 主键，所以得查询
    group = db.session.query(Group).first()
    group_user = db.session.query(GroupUser).first()

    group_user_relation = GroupUserRelation(platform=platform,
                                            group_db_id=group.id, user_db_id=group_user.id,
                                            is_admin=True, is_owner=True)
    db.session.add(group_user_relation)
    db.session.commit()
    return user


def login(client):
    resp: Response = client.post(url_for("session.SessionView"), json={
        "username": username,
        "password": password,
        "remember_me": False
    })

    return resp
