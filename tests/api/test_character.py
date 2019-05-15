# -*- coding: utf-8 -*-

"""
测试 'api.characters'
"""
import json
import pytest
from flask import Response, url_for
from flask.testing import FlaskClient

from tests.conftest import login, group_id, platform


@pytest.mark.usefixtures("user", "group_admin")
def test_post_table_query(client: FlaskClient):
    login(client)

    payload = {
        "version": "0.0.1",
        "table_name": "小鹤音形拆字表",
        "table_type": "xhup",
        "table": """比：　bi bibb*=拆分：　比左 匕=首末：　比左 匕=编码：　b  b
顷：　qkb qkbr=拆分：　比左 一 ノ 冂 人=首末：　比左 人=编码：　b  r
皆：　jpb jpbb=拆分：　比左 匕 白=首末：　比左 白=编码：　b  b""",
        "group_id": group_id,
        "platform": platform,
    }
    resp: Response = client.post(url_for("characters.TableView"), json=payload)

    assert resp.status_code == 201
    assert resp.json['version'] == payload['version']

    resp_2: Response = client.get(url_for("characters.CharView"), json={
        "char": "比",
        "version": "0.0.1",
        "table_name": "小鹤音形拆字表"
    })

    info = resp_2.json['info']
    assert info['codes'] == "bi bibb*"
    assert info['split'] == '比左 匕'
    assert info['other_info'] == {'编码': 'b b', '首末': '比左 匕'}
