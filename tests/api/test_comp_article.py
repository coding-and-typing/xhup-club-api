# -*- coding: utf-8 -*-

"""
测试 'api.comp_article'
"""

import json
import pytest
from flask import Response, url_for
from flask.testing import FlaskClient

from tests.conftest import login, group_id, platform, test_text


@pytest.mark.usefixtures("group_admin")
def test_comp_article_box(user, client: FlaskClient):
    login(client)

    # 1. 给定文档
    payload = {
        "content_type": "given_text",  # 给定文档
        "length": 500,
        # "delta": 30,  # 默认就是 30
        "count": 10,  # 添加赛文的最大篇数
        "content_subtype": "小说",  # 文档类型为小说
        "title": "青铜葵花",
        "text": test_text,
        # "separator": "",  # 如果提前用分割符分好段了的话
    }
    resp = client.post(url_for("comp_article.CompArticleBoxView"), json=payload)
    assert resp.status_code == 201
    assert resp.json == {
        "box_id": 1,
        'content_type': "小说",
        "count": 10
    }

    # 2. 随机散文
    payload = {
        "content_type": "random_article",  # 给定文档
        "length": 500,
        "count": 10,  # 添加赛文的最大篇数
    }
    resp = client.post(url_for("comp_article.CompArticleBoxView"), json=payload)
    assert resp.status_code == 201
    assert resp.json == {
        "box_id": 2,
        'content_type': "散文",
        "count": 10
    }

    # 3. 乱序单字
    payload = {
        "content_type": "shuffle_chars",  # 给定文档
        "length": 80,
        "count": 10,  # 添加赛文的最大篇数
        "content_subtype": "top_500"
    }
    resp = client.post(url_for("comp_article.CompArticleBoxView"), json=payload)
    assert resp.status_code == 201
    assert resp.json == {
        "box_id": 3,
        'content_type': "单字前五百",
        "count": 10
    }


