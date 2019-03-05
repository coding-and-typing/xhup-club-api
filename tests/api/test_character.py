# -*- coding: utf-8 -*-

"""
测试 'api.characters'
"""

import pytest
from flask import Response, url_for
from flask.testing import FlaskClient

from app.models import Group, GroupUser, GroupUserRelation
from tests.conftest import username, password

platform = 'qq'


@pytest.fixture
def group_admin(db, user):
    """使 user 成为测试群的群管理"""
    group = Group(platform=platform, group_id='12354321', group_name="测试群")
    group_user = GroupUser(platform=platform, username="测试管理员", main_user_id=user.id)
    group_user_relation = GroupUserRelation(platform=platform, group_db_id=group.id, user_db_id=group_user.id)

    db.session.add_all([group, group_user, group_user_relation])
    db.session.commit()
    return user


def login(client):
    resp: Response = client.post(url_for("session.SessionView"), json={
        "username": username,
        "password": password,
        "remember_me": False
    })

    return resp


@pytest.mark.usefixtures("group_admin")
def test_post_table(client: FlaskClient, user):
    login(client)

    payload = {
        "version": "0.0.1",
        "table_name": "小鹤音形拆字表",

        "table": "",
    }
    resp: Response = client.post(url_for("characters.TableView"))

