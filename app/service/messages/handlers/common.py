# -*- coding: utf-8 -*-
import functools
import logging
from typing import List

import re

from app import utils
from app.service.messages import dispatcher, as_command_handler, as_regex_handler, as_at_me_handler
from app.service.messages.handler import Handler
from app.service.words.character import get_info
from app.utils.text import split_text_by_length, generate_comp_content
from app.utils.web import daily_article, char_zdict_url

logger = logging.getLogger(__name__)


@as_command_handler(command="帮助",
                    weight=300,
                    prefix=("?", "？"),
                    arg_primary={
                        "name": "功能",
                        "type": str,
                        "required": False,
                        "help": "显示某功能的说明"
                    })
def usage_handler(data, session, args):
    """查看帮助信息
    “？帮助” ：显示所有支持的功能
    ------
    :param data:
    :param session:
    :param args:
    :return:
    """
    reply = dict()

    handlers: List[Handler] = dispatcher.get_handlers(data)
    fname = args['primary']  # function name
    if not fname:  # 返回所有功能的 usage
        handler_names = set()
        handlers_uniq = []
        for h in handlers:
            # 同一个 handler 可能会注册了多个命令（比如 talk），这里做去重工作
            if h.name not in handler_names:
                handler_names.add(h.name)
                handlers_uniq.append(h)

        usages = (f"{i}. {h.synopsis}" for i, h in enumerate(handlers_uniq))
        reply['text'] = "\n".join(usages)

    # 通过 fname 查找对应的 function
    for handler in handlers:
        if handler.name == fname:
            reply['text'] = handler.usage

    return reply


def talk_handler(data, session, message):
    """和机器人聊天
    1. 在群内 @ 我
    2. 信息以“：”开头，例如“：你好”
    ---
    :param data:
    :param session:
    :param message:
    :return:
    """
    group_id = message['group']['id'] if message['type'] == "group" else None

    reply = dict()
    text = re.sub(r"^(?:\:|：)", '', message['text'])  # 对
    reply['text'] = utils.web.talk(text,
                                   message['user']['id'],
                                   group_id)

    if group_id:
        reply['at_members'] = [message['user']['id'], ]
    return reply


at_me_talk_handler = as_at_me_handler(weight=300, name="聊天", pass_message=True)(talk_handler)
regex_talk_handler = as_regex_handler(
    re.compile(r"(?:\:|：)\S+.*"),
    weight=300, name="聊天", pass_message=True)(talk_handler)


@as_regex_handler(
    re.compile(r"(?:\?|？)(?P<char>\S)"),
    weight=300, name="查字", pass_groupdict=True)
def xhup_char_query_handler(data, session, groupdict):
    """查询小鹤双拼拆字表
        用法：“？字”
    ------
    :param data:
    :param session:
    :param groupdict:
    :return:
    """
    info = get_info(groupdict['char'], "小鹤音形拆字表")
    return {"text": '\n'.join((
        f"{info.char}：　{info.codes}",
        f"拆分：　{info.split}",
        f"首末：　{info.other_info['首末']}",
        f"编码：　{info.other_info['编码']}",
        f"汉典：{char_zdict_url(info.char)}",
    ))

    }


def _daily_article_handler_maker(random=False):
    def handler(data, session, args, message):
        """每天一篇赛文
        来自网站《每日一文》
        :param data:
        :param session:
        :param args:
        :param message:
        :return:
        """
        article = daily_article.get_article(random=random)
        article['content'] = list(split_text_by_length(article['content'],
                                                       length=args['primary']))
        segment_num = 1
        article['segment_len'] = args['primary']
        session.set("article", article)
        session.set("segment_num", segment_num)

        session.set("user_id", message['user']['id'])  # 用户 id
        session.set("username", message['user']['nickname'])

        return {"text": generate_comp_content(
            content=article['content'][segment_num - 1],
            title=article['title'],
            sub_title=article['sub_title'],
            author=article['author'],
            content_type=article['content_type'],
            segment_num=segment_num,
        )}

    return handler


daily_article_handler = as_command_handler(command="每日一文",
                                           weight=300,
                                           prefix=("?", "？"),
                                           arg_primary={
                                               "name": "字数",
                                               "type": int,
                                               "default": 300,
                                               "required": False,
                                               "help": "每段赛文的大概字数"
                                           },
                                           pass_message=True)(_daily_article_handler_maker(random=False))

random_article_handler = as_command_handler(command="随机一文",
                                            weight=300,
                                            prefix=("?", "？"),
                                            arg_primary={
                                                "name": "字数",
                                                "type": int,
                                                "default": 300,
                                                "required": False,
                                                "help": "每段赛文的大概字数"
                                            },
                                            pass_message=True)(_daily_article_handler_maker(random=True))


@as_command_handler(command="下一段",
                    weight=300,
                    prefix=("?", "？"), pass_message=True)
def next_segment_handler(data, session, args, message):
    """下一段

    :param data:
    :param session:
    :param args:
    :return:
    """
    article = session.get("article")
    segment_num = session.get("segment_num")
    user_id = session.get("user_id")
    # 如果当前没有跟打赛文
    if article is None or segment_num is None:
        return {"text": "请先开始跟打。\n举例：「？赛文」或「？每日一文」"}
    elif user_id != message['user']['id']:
        return {"text": "请先等待群友跟打完毕，或者新开赛文。\n举例：「？赛文」或「？每日一文」"}

    # 如果已经跟打完整篇文章
    if segment_num == len(article['content']):
        session.destroy()  # 销毁当前 session
        return {"text": f"《{article['title']}》跟打完毕！"}

    segment_num += 1  # 下一段
    session.set("segment_num", segment_num)
    return {"text": generate_comp_content(
        content=article['content'][segment_num - 1],
        title=article['title'],
        sub_title=article['sub_title'],
        author=article['author'],
        content_type=article['content_type'],
        segment_num=segment_num,
    )}


@as_command_handler(command="跟打状态",
                    weight=300,
                    prefix=("?", "？"), )
def status_handler(data, session, args):
    """跟打状态

    ---
    :param data:
    :param session:
    :param args:
    :return:
    """
    article = session.get("article")
    segment_num = session.get("segment_num")
    username = session.get("username")
    # 如果当前没有跟打赛文
    if article is None or segment_num is None:
        return {"text": "请先开始跟打。\n举例：「？赛文」或「？每日一文」"}
    else:
        segment_len = article['segment_len']
        return {"text":
                    f"群友 {username} 正在跟打《{article['title']}》\n" +
                    (f"每段字数：{segment_len}\n" if segment_len else "") +
                    f"共 {len(article['content'])} 段，当前位置：第 {segment_num} 段\n"
                    f"\n回复「？结束」结束跟打。"}


@as_command_handler(command="结束",
                    weight=300,
                    prefix=("?", "？"), )
def destroy_session_handler(data, session, args):
    """结束跟打

    ---
    :param data:
    :param session:
    :param args:
    :return:
    """
    session.destroy()
    return {"text": "结束跟打。"}


@as_command_handler(command="群组绑定",
                    weight=300,
                    prefix=("?", "？"),
                    arg_primary={
                        "name": "验证码",
                        "type": str,
                        "required": False,
                        "help": "用于群组绑定"
                    })
def group_bind_handler(data, session, args):
    """群组绑定

    ---
    :param data:
    :param session:
    :return:
    """


def typing_score(data, session, message):
    """跟打成绩记录

    ------
    :param data:
    :param session:
    :param message:
    :return:
    """
    # TODO 待完成
    pass


# 添加默认 handlers
# 1. 帮助命令
dispatcher.add_handler(usage_handler, platform="default", group_id="group")
dispatcher.add_handler(usage_handler, platform="default", group_id="private")

# 2. 聊天机器人
dispatcher.add_handler(at_me_talk_handler, platform="default", group_id="group")  # 只有群内才能 at

dispatcher.add_handler(regex_talk_handler, platform="default", group_id="group")
dispatcher.add_handler(regex_talk_handler, platform="default", group_id="private")

# 3. 小鹤拆字
dispatcher.add_handler(xhup_char_query_handler, platform="default", group_id="group")
dispatcher.add_handler(xhup_char_query_handler, platform="default", group_id="private")

# 4. 每日一文和随机一文
dispatcher.add_handler(daily_article_handler, platform="default", group_id="group")
dispatcher.add_handler(daily_article_handler, platform="default", group_id="private")

dispatcher.add_handler(random_article_handler, platform="default", group_id="group")
dispatcher.add_handler(random_article_handler, platform="default", group_id="private")

# 5. 下一段与跟打状态
dispatcher.add_handler(next_segment_handler, platform="default", group_id="group")
dispatcher.add_handler(next_segment_handler, platform="default", group_id="private")

dispatcher.add_handler(status_handler, platform="default", group_id="group")
dispatcher.add_handler(status_handler, platform="default", group_id="private")

dispatcher.add_handler(destroy_session_handler, platform="default", group_id="group")
dispatcher.add_handler(destroy_session_handler, platform="default", group_id="private")

# 6. 跟打成绩记录


# 7. 群组绑定
