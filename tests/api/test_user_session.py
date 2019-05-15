# -*- coding: utf-8 -*-

"""
测试 'api.user' 和 'api.session'
"""

import pytest
from flask import Response, url_for
from flask.testing import FlaskClient

from app.models import MainUser
from tests.conftest import username, password, email, login


class TestSession(object):
    """测试登录登出"""

    @pytest.mark.usefixtures("user")
    def test_login(self, client: FlaskClient):
        resp = login(client)

        assert resp.status_code == 201
        assert resp.json['email'] == email

    @pytest.mark.usefixtures("user")
    def test_logout(self, client: FlaskClient):
        login(client)

        resp: Response = client.delete(url_for("session.SessionView"))

        assert resp.status_code == 204

    @pytest.mark.usefixtures("user")
    def test_get(self, client: FlaskClient):
        login(client)

        resp: Response = client.get(url_for("session.SessionView"))

        assert resp.status_code == 200
        assert resp.json['username'] == username
        assert resp.json['email'] == email


class TestUser(object):

    @pytest.mark.usefixtures("db")
    def test_create(self, client: FlaskClient):
        """
        测试用户注册
        """
        resp: Response = client.post(url_for("user.UserView"), json={
            "username": username,
            "email": email,
            "password": password
        })

        assert resp.status_code == 201
        assert resp.json['username'] == username
        assert resp.json['email'] == email

    @pytest.mark.usefixtures("user")
    def test_create_conflict(self, client: FlaskClient):
        resp: Response = client.post(url_for("user.UserView"), json={
            "username": username,
            "email": email,
            "password": password
        })

        assert resp.status_code == 409

    @pytest.mark.usefixtures("user")
    def test_delete(self,  client: FlaskClient, db):
        """
        测试删除账号
        """
        login(client)

        assert db.session.query(MainUser).filter_by(username=username).first() is not None

        # 删除账号
        resp: Response = client.delete(url_for("user.UserView"), json={
            "password": password
        })

        assert resp.status_code == 204
        assert db.session.query(MainUser).filter_by(username=username).first() is None

    @pytest.mark.usefixtures("user")
    def test_get(self,  client: FlaskClient):
        """
        测试获取账号信息
        """
        login(client)

        resp: Response = client.get(url_for("user.UserView"))

        assert resp.status_code == 200
        assert resp.json['username'] == username
        assert resp.json['email'] == email


