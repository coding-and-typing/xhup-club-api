# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import os

import pytest

# 测试环境
os.environ['XHUP_ENV'] = 'test'

from app import create_app
from app import db as _db
from app.models import MainUser


@pytest.fixture
def app():
    """An application for the tests."""
    _app = create_app()
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
