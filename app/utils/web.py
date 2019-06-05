# -*- coding: utf-8 -*-
import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup
from urllib import parse
from urllib.parse import SplitResult

from app import current_config, utils
from app.utils.text import split_text_by_length

"""
使用网络上其他 api 的工具函数
"""

logger = logging.getLogger(__name__)


def short_the_url(url: str):
    """使用短链服务"""
    parse.urlsplit(url)  # 解析失败会抛 error

    params = {
        'token': current_config.SHORT_URL_TOKEN,  # 美人提供的接口，这个是token
        'url': url,
    }
    result = requests.get(current_config.SHORT_URL_API, params=params)

    return result.json()["short_url"]


def char_zdict_url(chars: str):
    """查询汉典"""
    return short_the_url('https://www.zdic.net/hans/' + parse.quote(chars))


def talk(message: str, user_id, group_id=None, username=None):
    """图灵聊天服务"""
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": message
            }
        },
        "userInfo": {
            "apiKey": current_config.TURING_KEY,
            "userId": user_id,
            "groupId": group_id,
            "userIdName": username,
        }
    }

    resp = requests.post(url=current_config.TURING_API, json=data).json()

    # 分析返回值
    code = resp['intent']["code"]
    if code < 10000:  # 异常
        logger.warning(f"图灵机器人异常，数据：{resp}")
        return "异常状况，即将崩坏。9 8 7..."

    codes_text_only = [  # 可以直接输出的 code
        10004,  # 聊天
        10008,  # 天气
        10009,  # 计算
        10010,  # 故事
        10011,  # 成语接龙
        10013,  # 百科
        10016,  # 快递查询
        10019,  # 日期
        10020,  # 翻译
        10022,  # 脑筋急转弯
        10030,  # 歇后语
        10031,  # 绕口令
        10032,  # 顺口溜
        10033,  # 邮编
        10034,  # 自定义语料库
        10041,  # 星座运势（包含多个）
    ]
    if code in codes_text_only:  # 可以直接输出
        return resp['results'][0]["values"]['text']

    return "暂不提供该功能"


class DailyArticle(object):
    """每日一文的 API"""

    def __init__(self):
        self.session = requests.session()
        url: SplitResult = parse.urlsplit(current_config.RANDOM_ARTICLE_API)
        self.session.headers = {
            "Host": url.netloc,
            "User-Agent": current_config.USER_AGENT
        }

    def get_article(self,
                    length: Optional[int] = None,  # 方案一：length + delta
                    delta: Optional[int] = 30,
                    max_length: Optional[int] = None,  # 方案二：直接确定长度上下限
                    min_length: Optional[int] = None,
                    cut_content: Optional[bool] = False,
                    random=True,
                    del_special_char=True):
        """随机一篇散文
        :param delta:
        :param length:
        :param max_length: 文章允许的最长长度。
        :param min_length: 文章允许的最短长度。比这还短就丢弃。
        :param cut_content: 如果文章过长，是否使用 split_text 做 cut 操作？

        :param random:
        :param del_special_char:
        :return: 文章
        """
        url = current_config.RANDOM_ARTICLE_API if random else current_config.DAILY_ARTICLE_API
        resp = self.session.get(url)
        bsObj = BeautifulSoup(resp.text, "html.parser")

        # 使用 class 属性匹配文章内容
        content = bsObj.find(attrs={"class": "article_text"}).getText()

        # 预处理文本
        content = utils.text.process_text_cn(content)

        # 检查文章长度是否符合要求
        if length:
            max_length = length + delta
            min_length = length - delta

        if min_length and len(content) < min_length:  # 如果给了最小长度，并且赛文短于这个长度
            return self.get_article(min_length, random, del_special_char)  # 重新获取文章

        if max_length and len(content) > max_length:
            if cut_content:  # 对文章内容做剪切
                content = next(split_text_by_length(
                    content, max_length=max_length, min_length=min_length))
            else:  # 不允许剪切文章，只好获取新文章了
                return self.get_article(min_length, random, del_special_char)  # 重新获取文章

        # 去除特殊字符
        special_chars = None
        if del_special_char:
            content = utils.text.del_special_char(content)
        else:
            special_chars = utils.text.special_chars(content)

        return {
            "content": content,
            "title": bsObj.h1.getText(),
            "sub_title": "随机一文" if random else "每日一文",
            "content_type": "散文",
            "author": bsObj.find(attrs={"class": "article_author"}).getText(),
            "special_chars": special_chars,
        }


daily_article = DailyArticle()
