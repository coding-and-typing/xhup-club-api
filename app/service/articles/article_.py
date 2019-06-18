# -*- coding: utf-8 -*-

"""
赛文添加相关
"""
from datetime import date, time, timedelta
import logging
from functools import reduce
from itertools import chain
from typing import Iterable

import random
from operator import add
from sqlalchemy import func

from app import current_config, db
from app.models import CompArticleBox, CompArticle, Group
from app.utils.common import group_each, iter_one_by_one, filter_truth
from app.utils.text import Chars, generate_articles_from_chars, split_text_by_length, split_text_by_sep, \
    process_text_en, process_text_cn, del_special_char
from app.utils.web import daily_article

logger = logging.getLogger(__name__)


def add_comp_article_box(data: dict, main_user):
    """添加候选赛文 box"""
    content_type = data['content_type']
    length = data['length']
    delta = data.get('delta', 30)  # 默认值 30
    count = data['count']

    # 1. 生成赛文
    if content_type == "random_article":
        content_type = "散文"
        articles = []

        for article in daily_article.get_random_articles(  # 1. 批量获取互不重复的随机散文
                count=count,
                length=length,
                delta=delta,
                cut_content=True):
            articles.append({
                "content": article.content,
                "title": article.title,
                "content_type": content_type,
            })
    elif content_type == "shuffle_chars":  # 2. 乱序单字
        content_type = data.get('content_subtype', '')
        if content_type not in Chars.top_chars:
            return 400, f"invalid choice! required in {Chars.top_chars}"

        chars_dict = Chars.top_chars[content_type]
        articles = generate_articles_from_chars(content_type, length, count, shuffle=True)
        content_type = chars_dict['name']  # 内容名称（例：单字前五百）
    elif content_type == "given_text":  # 3. 使用给定的文档生成赛文
        content_type = data['content_subtype']
        title = data['title']
        text = data['text']

        # a. 对文本做处理
        # （中文：去空格去换行，英文：去换行，合并连续的空格。全半角转换，去除特殊字符）
        if data.get('en') is True:  # 内容为英文
            text = process_text_en(text)
            text = del_special_char(text, en=True)  # 去除特殊字符
        else:
            text = process_text_cn(text)
            text = del_special_char(text)  # 去除特殊字符

        # b. 文本切分（按长度还是按给定的分割符）
        separator = data.get("separator")
        if not separator:
            text_generator = split_text_by_length(text, length, delta, ignore_=True)
        else:
            text_generator = iter(split_text_by_sep(text, separator))  # 使用预先插入的切分符号进行切分。

        if isinstance(count, int) and count > 0:
            text_generator_all = text_generator  # 重命名，以防止无限递归
            text_generator = (next(text_generator_all) for _ in range(count))

        articles = ({
            "content": content,
            "title": title,
            "content_type": content_type,  # 散文、政论、小说、混合赛文等
        } for content in text_generator)
    else:
        return 400, "invalid content_type!"

    # 2. 插入数据库
    next_box_id = 1 + db.session.query(CompArticleBox.box_id) \
        .filter_by(main_user_id=main_user.id).distinct().count()  # id 从 1 开始（1 + 0）
    items = [CompArticleBox(**article,
                            main_user_id=main_user.id,
                            box_id=next_box_id)
             for article in articles]

    # TODO 去重！
    db.session.add_all(items)
    db.session.commit()

    return 201, {
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


def generate_comp_articles(comp_articles: Iterable,
                           main_user,
                           group_db_id,
                           start_number: int,
                           start_date: date,
                           start_time: time,
                           end_time: time,
                           comp_type: str,
                           date_step: timedelta = timedelta(days=1),
                           ):
    """

    :param comp_articles: 赛文列表
    :param main_user: 当前用户（其实可以直接 import current_user）
    :param group_db_id: 群号
    :param start_number: 起始期数
    :param start_date: 起始日期
    :param start_time: 赛文开始时间
    :param end_time: 赛文结束时间
    :param comp_type: 赛事类型
    :param date_step: 赛事间隔（每这么多天一篇赛文）
    :return:
    """
    date_ = start_date
    number = start_number
    for article in comp_articles:
        yield CompArticle(
            title=article['title'],
            content=article['content'],
            content_type=article['content_type'],

            producer=main_user.username,  # 用户的用户名

            date_=date_,
            start_time=start_time,
            end_time=end_time,

            number=number,
            comp_type=comp_type,
            group_db_id=group_db_id,
        )

        number += 1
        date_ += date_step


def add_comp_articles_from_box(data: dict, main_user):
    """候选赛文全部转正"""
    box_count = db.session.query(func.count(CompArticleBox.box_id)) \
        .filter_by(main_user_id=main_user.id).scalar()
    boxes = []
    for i in range(1, box_count + 1):
        comp_articles = db.session.query(CompArticleBox) \
            .filter_by(main_user_id=main_user.id, box_id=i).all()
        boxes.append(comp_articles)

    count = reduce(add, (len(it) for it in boxes))

    # 1. 赛文混合
    mix_mode = data['mix_mode']
    if mix_mode == "proportionally":  # 按比例分配
        # 1) 先分组
        scale_list = data['scale_list']
        for i, box in enumerate(boxes):
            boxes[i] = group_each(box, scale_list[i], allow_none=True)

        # 2) 再混合
        boxes = iter_one_by_one(boxes, allow_none=True)  # 分组混合
        boxes = filter_truth(boxes)  # 过滤掉 None 值
        comp_articles = chain.from_iterable(boxes)  # flat 化
        comp_articles = list(filter_truth(comp_articles))  # 再次过滤 None 值
    else:
        comp_articles = list(chain(*boxes))  # 按序首尾相连，即 top2down
        if mix_mode == "random":
            random.shuffle(comp_articles)  # 乱序
        elif mix_mode != "top2down":
            return 400, "invalid mix_mod!"

    # 2. 添加到 CompArticle 表
    group = db.session.query(Group) \
        .filter_by(group_id=data['group_id'], platform=data['platform']).first()
    items = generate_comp_articles(comp_articles,
                                   main_user=main_user,
                                   start_date=data['start_date'],
                                   start_time=data['start_time'],
                                   end_time=data['end_time'],

                                   start_number=data['start_number'],
                                   comp_type=data['comp_type'],
                                   group_db_id=group.id)

    # TODO 添加之前，确认每篇文章都没有和已有的赛文重复！！
    db.session.add_all(items)
    db.session.commit()
    return 200, {
        "count": count,
        "start_date": data['start_date'],
        "end_date": data['start_date'] + timedelta(days=count)
    }
