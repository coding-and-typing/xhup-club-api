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
group_id = '12354321'
user_id = "1233231"


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


@pytest.mark.usefixtures("group_admin", "user")
def test_post_table(client: FlaskClient):
    login(client)

    payload = {
        "version": "0.0.1",
        "table_name": "小鹤音形拆字表",
        "table_type": "xhup",
        "table": """比：　bi bibb*=拆分：　比左 匕=首末：　比左 匕=编码：　b  b
顷：　qkb qkbr=拆分：　比左 一 ノ 冂 人=首末：　比左 人=编码：　b  r
皆：　jpb jpbb=拆分：　比左 匕 白=首末：　比左 白=编码：　b  b""",
        "group_id": group_id,
        "group_platform": platform,
    }
    resp: Response = client.post(url_for("characters.TableView"), json=payload)

    assert resp.status_code == 201

