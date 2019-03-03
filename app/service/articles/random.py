# -*- coding: utf-8 -*-
import time

import requests
from bs4 import BeautifulSoup
from urllib import parse
from urllib.parse import SplitResult

from app import current_config

"""
随机一文，暂时是使用的每日一文的 api

TODO  1. 重构代码  2. 批量抓取、插入数据
3. 得检查文章处理后，是不是还有特殊字符
"""

#
# def split_text(text: str,
#                separator: str = None,
#                length: int = None,
#                del_white_chars: bool = True,
#                substitute_punc: bool = True,
#                shuffle=False,
#                error_interval: int = 20):
#     """
#     文档切分，切分方式有两种：
#         separator 指定分隔符,比如指定"="，则会以"="重复三次以上为分隔符
#         length 指定长度
#
#     :param text: str 文本
#     :param separator: 指定分隔符
#     :param length: 指定长度
#     :param del_white_chars: 是否删除空白符号，比如空格、换行
#     :param substitute_punc: 是否将半角标点替换成全角
#     :param shuffle: 文本乱序，添加单字训练文本时需要
#     :param error_interval: 切分允许的误差量，切分得到的文本长度允许在 length +/- error_interval 以内
#     :return:
#     """
#     articles = []
#
#     # 预处理文本
#     text = utils.preprocess_text(text, del_white_chars, substitute_punc)
#
#     # 乱序
#     if shuffle:
#         text = utils.shuffle_text(text)
#
#     if separator:  # 使用分隔符切分
#         articles.extend(re.split(rf"({separator}){{3,}}", text))
#     elif length:  # 指定长度
#         articles.extend(split_text_by_length(text, length, error_interval=error_interval))
#     else:  # 两个都没指定，异常
#         raise AttributeError("必须指定分隔符或分割长度两者之一！")
#
#     return articles
#
#
# def split_text_by_length(text: str, length: int,
#                          error_interval: int = 30, recursive=True):
#     """
#     根据给定的长度切分文本
#     :param recursive: 是否递归切分
#     :param text: 文本
#     :param length: 切分长度
#     :param error_interval: 允许的误差量，切分得到的文本长度允许在 length +/- error_interval 以内
#     :return: list  [文章，剩余部分]
#     """
#     if len(text) <= length:
#         return [text]
#
#     up = min(length + error_interval - 1, len(text) - 1)  # 文章长度上限
#     down = max(length - error_interval - 1, 0)  # 文章长度下限
#
#     s = text[:up]
#     matcher = re.search(r"[”。！？；’～】）]", s[::-1])  # reverse 然后搜索.
#     matcher2 = re.search(r"，", s[::-1])  # reverse 然后搜索，用逗号是中策
#
#     index = -1  # -1 表示仍未找到切分点
#     if matcher:  # 上策
#         ind = up - matcher.start()  # up - start 得到未反转时该字符的索引（右边是开区间）
#         if ind >= down:
#             index = ind  # 找到切分点
#     if index == -1 and matcher2:  # 中策
#         ind = up - matcher2.start()
#         if ind >= down:
#             index = ind  # 找到切分点
#     if index == -1:
#             index = length  # 否则直接切分，下下策
#
#     # 递归切分
#     if recursive:
#         other_parts = split_text_by_length(text[index:], length)
#         return [text[:index], *other_parts]
#     else:
#         return [text[:index], text[index:]]
#
#
# def get_articles_from_text(text: str,
#                            title: str,
#                            text_type: str,
#                            **kwargs):
#     """
#     从本地文档批量添加赛文
#     :param text: 文本
#     :param title: 文本标题
#     :param text_type: 文档类型（散文、单字、政论、小说）
#     :param kwargs: 控制切分的可选参数
#     :return: article 的列表
#     """
#     contents = split_text(text, **kwargs)
#     return [{
#         "content": content,
#         "title": title,
#         "content_type": text_type,
#     } for content in contents]
#
#
#
# class RandomArticle(object):
#     def __init__(self):
#         self.session = requests.session()
#         url: SplitResult = parse.urlsplit(current_config.RANDOM_ARTICLE_API)
#         self.session.headers = {
#             "Host": url.netloc,
#             "User-Agent": current_config.USER_AGENT
#         }
#
#         # 先获取一下 cookie
#         self.session.get(current_config.RANDOM_ARTICLE_API)
#
#     def get_random_article(self, length: int = 1000,
#                            del_white_chars: bool = True,
#                            substitute_punc: bool = True):
#         """
#         随机一篇散文
#         :param length: 文章截取的长度
#         :param del_white_chars: 去除空白字符，默认 True
#         :param substitute_punc: 是否将半角标点替换成全角
#         :return: 文章
#         """
#         resp = self.session.get(current_config.RANDOM_ARTICLE_API)
#         bsObj = BeautifulSoup(resp.text, "html.parser")
#
#         # 使用 class 属性匹配文章内容
#         content = bsObj.find(attrs={"class": "article_text"}).getText()
#
#         # 预处理文本
#         content = utils.preprocess_text(content, del_white_chars, substitute_punc)
#
#         # 切分
#         content = split_text_by_length(content, length)[0]
#
#         return {
#             "content": content,
#             "title": bsObj.h1.getText(),
#             "content_type": "散文",
#             # "producer": bsObj.find(attrs={"class": "article_author"}).getText(),  # 赛文制作人，这里直接用散文作者了
#         }
#
#     def get_random_articles(self, count: int, time_step=0.8, **kwargs):
#         """
#         获取多篇随机散文
#         :param count: 获取数量
#         :param time_step: 随机休眠的间隔
#         :return: article list
#         """
#         article_box = []
#         for i in range(count):
#             article_box.append(self.get_random_article(**kwargs))
#             time.sleep(time_step)
#
#         return article_box


