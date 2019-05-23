# -*- coding: utf-8 -*-

"""
赛文添加相关
"""
from itertools import cycle

from sqlalchemy import func

from app import current_config, db
from app.models import CompArticleBox
from app.utils.text import Chars, generate_articles_from_chars, split_text_by_length
from app.utils.web import daily_article


def add_comp_article_box(data: dict, main_user):
    """添加候选赛文 box"""
    content_type = data['content_type']
    length = data['length']
    delta = data['delta']
    count = data['count']

    # 1. 生成赛文
    if content_type == "random_article":
        articles = [daily_article.get_article(
            length=length,
            delta=delta,
            cut_content=True)
            for _ in range(count)]
    elif content_type == "shuffle_chars":
        content_type = data.get('content_type_2', '')
        if content_type not in Chars.top_chars:
            return 400, f"invalid choice! required in {Chars.top_chars}"

        articles = generate_articles_from_chars(content_type, length, count, shuffle=True)
    elif content_type == "given_text":
        title = data['title']
        text = data['text']
        content_type = data['content_type_2']

        articles = [{
            "content": str_,
            "title": title,
            "content_type": content_type,  # 散文、政论、小说、混合赛文等
        } for str_ in split_text_by_length(text, length, delta, ignore_=True)]
    else:
        return 400, "invalid content_type!"

    # 2. 插入数据库
    next_box_id = 1 + db.session.query(func.count(CompArticleBox.box_id)) \
        .filter_by(main_user_id=main_user.id).scalar()  # 获取标量
    items = [CompArticleBox(**article,
                            main_user_id=main_user.id,
                            box_id=next_box_id)
             for article in articles]

    db.session.add_all(items)
    db.session.commit()

    return 200, {
        "box_id": next_box_id,
        'content_type': content_type,
        "count": len(items)
    }


def delete_comp_article_box(data: dict, main_user):
    db.session.query(CompArticleBox) \
        .filter_by(**data, main_user_id=main_user.id) \
        .delete()
    db.session.commit()
