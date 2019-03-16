# -*- coding: utf-8 -*-
from itertools import chain

import logging
import re
import random
import string

import chardet
from typing import Iterable

from app import current_config

"""
文字处理相关的工具函数
"""

logger = logging.getLogger(__name__)


class Chars:
    """字符相关"""

    # 1. 可以转换的全角字符，跟打前必须转换成半角
    # fl 是 full width （全宽）的缩写
    fl_ascii_lowercase = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
    fl_ascii_uppercase = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
    fl_ascii_letters = fl_ascii_lowercase + fl_ascii_uppercase
    fl_digits = "０１２３４５６７８９"

    fl_punctuation = r"""＃％＆＋－＝＠｀｛｜｝．"""

    # 全角与半角的对应表（不论是中文还是英文，都要使用此表做转换）
    fl_table = str.maketrans(
        dict(zip(fl_ascii_letters + fl_digits + fl_punctuation,  # 全角
                 string.ascii_letters + string.digits + "#%&+-=@`{|}."))  # 半角
    )

    # 2. 中英标点对照表（可相互转换）
    punctuation_table = {
        ',': '，',
        '.': '。',
        '?': '？',
        '!': '！',
        ';': '；',
        ':': '：',
        '(': '（',
        ')': '）',
        '[': '【',
        ']': '】',
        '~': '～',
        "<": "《",
        ">": "》",
        "*": "×",
    }

    # 3. 中文文章文本替换，要使用的转换表
    table_cn = str.maketrans(punctuation_table)  # 要用 str.maketrans

    # 4. 处理完成后，中文文章允许包含的标点
    SYMBOLS_CN = frozenset("".join(punctuation_table.values())
                           + "、‘’“”{}《》〈〉〔〕|`@#￥%……&×——+-=·"  # 中英难以对应的标点（或者中英都使用同样的）
                           + string.digits + string.ascii_letters)  # 中文也使用半角标点、字母

    # 5. 特殊字符中，可以转换成非特殊字符的
    SPECIAL_SPACE = "\u2001" + "\u200a" + "\u2009"  # 三个特殊空格
    SPECIAL_MIDDLE_LINE = '―' + "─" + "—"

    # 6. 未做处理前，文章中允许出现的标点
    SYMBOLS_ALL = frozenset(chain(string.printable,
                                  SYMBOLS_CN,
                                  SPECIAL_SPACE,
                                  SPECIAL_MIDDLE_LINE))

    # 7. 处理完成后，中文文章允许包含的所有字符
    UNICODE_CN = current_config.CHARS.union(SYMBOLS_CN)

    # 8. 处理之前，中文文章允许包含的所有字符
    UNICODE_ALL = current_config.CHARS.union(SYMBOLS_ALL)


def auto_decode(content: bytes):
    """检测编码，读取文件"""
    detect = chardet.detect(content)  # 检测编码
    if detect['confidence'] < 0.7:
        logger.warning(f"可信度小于 0.7：{detect['confidence']}")
    else:
        logger.debug(f"可信度：{detect['confidence']}")

    return content.decode(detect['encoding'])


def shuffle_text(text: str):
    """文本乱序，添加单字赛文时可能需要"""
    text_list = [*text]
    random.shuffle(text_list)

    return "".join(text_list)


def del_white_chars(s: str):
    """去除所有空白字符
    包括几个特殊空格
    """
    # \s 表示任意空白字符（tab space \n）
    return re.sub(rf"[\s{Chars.SPECIAL_SPACE}]", "", s)


def sub_punctuation(text: str):
    """
    将文本中的半角标点转换成全角标点
    :param text: 文本
    :return: 转换后的文本
    """
    # 全角转半角
    text = text.translate(Chars.fl_table)
    # 英文转中文
    text = text.translate(Chars.table_cn)

    # 破折号
    text = re.sub(rf"[{Chars.SPECIAL_MIDDLE_LINE}]+", "——", text)
    # 省略号
    text = re.sub(r"⋯+|\.{3,6}", "……", text)

    return text


def process_text_cn(text: str):
    """中文文本处理"""
    text = del_white_chars(text)
    text = sub_punctuation(text)

    return text


def special_chars(text: str):
    """返回 text 中的特殊字符"""
    text_set = frozenset(text)

    return text_set.difference(Chars.UNICODE_CN)


def search_split_pos(text: str,
                     keys: Iterable = "”’】）。！？；～…"):
    """查找最适合切分的位置"""

    def rindex(c: str):
        try:
            return text.rindex(c)
        except ValueError:
            return -1

    return max(map(rindex, keys)) + 1  # 加 1 是因为，python 的切分，不包括右边的端点


def split_text(text: str,
               max_length: int,
               minimal_length: int):
    """
    根据给定的长度切分文本
    :param text: 文本
    :param max_length: 切分长度
    :param minimal_length: 文章允许的最短长度。比这还短就丢弃。
    :return : 迭代器，每次返回切分出来的那一段
    """
    while len(text) > max_length:
        s = text[:max_length]
        index = search_split_pos(s)  # 上策
        if index < minimal_length:
            index = search_split_pos(s, keys="，")  # 中策
        if index == -1:
            index = (max_length + minimal_length) // 2  # 直接切分，下下策

        yield text[:index]
        text = text[index:]
    else:
        if len(text) < minimal_length:
            return  # 结束迭代

        yield text
