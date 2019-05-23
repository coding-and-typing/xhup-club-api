# -*- coding: utf-8 -*-

"""
赛文添加相关
"""
from itertools import cycle

from sqlalchemy import func

from app import current_config, db
from app.models import CompArticleBox
from app.utils.text import Chars, generate_articles_from_chars, split_text_by_length, split_text_by_sep, \
    process_text_en, process_text_cn, del_special_char
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

        # 1. 对文本做处理
        # （中文：去空格去换行，英文：去换行，合并连续的空格。全半角转换，去除特殊字符）
        if data.get('en') is True:  # 内容为英文
            text = process_text_en(text)
            text = del_special_char(text, en=True)  # 去除特殊字符
        else:
            text = process_text_cn(text)
            text = del_special_char(text)  # 去除特殊字符

        # 2. 文本切分（按长度还是按给定的分割符）
        separator = data.get("separator")
        if not separator:
            text_list = split_text_by_length(text, length, delta, ignore_=True)
        else:
            text_list = split_text_by_sep(text, separator)  # 使用预先插入的切分符号进行切分。
        articles = [{
            "content": str_,
            "title": title,
            "content_type": content_type,  # 散文、政论、小说、混合赛文等
        } for str_ in text_list]
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
    """删除候选赛文盒"""
    db.session.query(CompArticleBox) \
        .filter_by(**data, main_user_id=main_user.id) \
        .delete()
    db.session.commit()


def add_comp_articles_from_box(data: dict, main_user):
    """候选赛文全部转正"""
    box_count = db.session.query(func.count(CompArticleBox.box_id)) \
        .filter_by(main_user_id=main_user.id).scalar()
    boxes = []
    for i in range(1, box_count+1):
        comp_articles = db.session.query(CompArticleBox) \
            .filter_by(main_user_id=main_user.id, box_id=i).all()
        boxes.append(comp_articles)

    # 1. 赛文混合

    # 2. 添加到 CompArticle 表
    pass


def sync_to_chaiwubi(data, main_user):
    """TODO 赛文同步到拆五笔赛文系统上"""
    pass
