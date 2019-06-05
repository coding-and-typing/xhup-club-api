# -*- coding: utf-8 -*-
from itertools import chain

import logging
import re
import random
import string
from datetime import datetime

import chardet
from typing import Iterable, Optional

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
        '[': '【',  # 「『
        ']': '】',  # 」』
        '~': '～',
        "<": "《",
        ">": "》",
        "*": "×",
    }

    # 3. 中文文章文本替换，要使用的转换表
    table_cn = str.maketrans(punctuation_table)  # 要用 str.maketrans

    table_en = str.maketrans(
        {val: key for key, val in punctuation_table.items()})  # 逆转一下

    # 英文中（用于跟打），空白字符只允许出现空格
    CHARS_EN = string.digits + string.ascii_letters + string.punctuation + ' '

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
    UNICODE_CN = current_config.CHARS_ALLOWED.union(SYMBOLS_CN)

    # 8. 处理之前，中文文章允许包含的所有字符
    UNICODE_ALL = current_config.CHARS_ALLOWED.union(SYMBOLS_ALL)

    # 9. 单字前几百
    top_chars = {
        'top_1500': {
            "chars": current_config.CHARS_TOP_1500,
            "title": "单字前一千五",
        },
        'top_500': {
            "chars": current_config.CHARS_TOP_500,
            "title": "单字前五百",
        },
        'middle_500': {
            "chars": current_config.CHARS_MIDDLE_500,
            "title": "单字中五百",
        },
        'last_500': {
            "chars": current_config.CHARS_LAST_500,
            "title": "单字后五百",
        },
    }


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


def cycle_str(string_, shuffle=True):
    """无限迭代器

    :param string_: 字符串
    :param shuffle: 是否乱序。（每循环完一次，都会重新 shuffle）
    :return:
    """
    while True:
        if shuffle:
            string_ = shuffle_text(string_)
        yield from string_
        yield from cycle_str(string_)


def del_white_chars(s: str, en=False):
    """去除所有空白字符
    包括几个特殊空格
    """
    # \s 表示任意空白字符（tab space \n）
    return re.sub(rf"[\s{Chars.SPECIAL_SPACE}]+",
                  " " if en else '',  # 英文模式下，保留非连续的空格。
                  s)


def sub_punctuation(text: str, en=False):
    """
    :param text: 文本
    :return: 转换后的文本
    """
    # 全角转半角，中英通用
    text = text.translate(Chars.fl_table)

    if not en:  # 中文，将文本中的半角标点转换成全角标点
        # 英文标点转中文标点
        text = text.translate(Chars.table_cn)

        # 破折号
        text = re.sub(rf"[{Chars.SPECIAL_MIDDLE_LINE}]+", "——", text)
        # 省略号
        text = re.sub(r"⋯+|\.{3,}|…+", "……", text)
    else:  # 英文
        # 中文标点转英文标点
        text = text.translate(Chars.table_en)

        # 替换成英文破折号
        text = re.sub(rf"[{Chars.SPECIAL_MIDDLE_LINE}]+", "-", text)
        # 替换成英文省略号（三个点）
        text = re.sub(r"⋯+|\.{3,}|…+", "...", text)

    return text


def process_text_cn(text: str):
    """中文文本处理"""
    text = del_white_chars(text)
    text = sub_punctuation(text)

    return text


def process_text_en(text: str):
    """英文文本处理"""
    text = del_white_chars(text, en=True)
    text = sub_punctuation(text, en=True)

    return text


def special_chars(text: str):
    """返回 text 中的特殊字符"""
    text_set = frozenset(text)

    return text_set.difference(Chars.UNICODE_CN)


def is_not_special_char(ch: str, en=False):
    if not en:  # 中文
        return ch in Chars.UNICODE_CN
    else:  # 英文
        return ch in Chars.CHARS_EN


def del_special_char(text, en=False):
    return ''.join(filter(lambda ch: is_not_special_char(ch, en),
                   text))


def search_split_pos(text: str,
                     keys: Iterable = "”’】）。！？；～…"):
    """查找最适合切分的位置"""

    def rindex(c: str):
        try:
            return text.rindex(c)
        except ValueError:
            return -1

    return max(map(rindex, keys)) + 1  # 加 1 是因为，python 的切分，不包括右边的端点


def split_text_by_length(text: str,
                         length: Optional[int] = None,  # 方案一：length + delta
                         delta: Optional[int] = 30,
                         max_length: Optional[int] = None,  # 方案二：直接确定长度上下限
                         min_length: Optional[int] = None,
                         ignore_=False):
    """
    根据给定的长度切分文本
    :param text: 文本
    :param delta:
    :param length:
    :param max_length: 文章允许的最长长度。
    :param min_length: 文章允许的最短长度。比这还短就丢弃。
    :return : 迭代器，每次返回切分出来的那一段
    :param ignore_: 如果最后一段太短，是否丢弃掉该段。默认不丢弃
    """
    if length:
        max_length = length + delta
        min_length = length - delta

    if not max_length or not min_length:
        logger.error(f"split_text_by_length 缺少必要参数！！！")
        return None

    while len(text) > max_length:
        s = text[:max_length]
        index = search_split_pos(s)  # 上策
        if index < min_length:
            index = search_split_pos(s, keys="，")  # 中策
        if index == -1:
            index = (max_length + min_length) // 2  # 直接切分，下下策

        yield text[:index]
        text = text[index:]
    else:
        if len(text) < min_length and ignore_:
            return  # 结束迭代

        yield text


def split_text_by_sep(text: str,
                      sep: str):
    """通过分隔符(separator)切分文本
        这适用于人工制作的赛文，使用工具批量添加的情况。

        e.g. 分隔符为 '-', 此函数会在所有 '---' 处分割文本，其中 '-' 需要重复三次以上
            分隔符也可以为多个字符，比如 '-#'，那么分割线应该是 '-#-#-#' 这样重复三次以上。
    """
    return re.split(rf"(?:{sep}){{3,}}", text)  # sep 重复三次以上


def generate_comp_content(content, title, sub_title, content_type, author, segment_num: int):
    """将 article 组装成跟打器可以识别的赛文格式

    :param content: 内容
    :param title: 文章标题
    :param sub_title: 子标题，日赛、周赛、每日赛文等
    :param content_type: 文章类型
    :param author: 作者
    :param segment_num: 文章段号
    :return:
    """
    date = datetime.now().date()
    return f"《{title}》{sub_title}第{date}期-作者：{author}\n" \
        f"{content}\n" \
        f"-----第{segment_num}段--xxx--c.sw.1.1\n" \
        f"本文由 {content_type} 组成"


def generate_articles_from_chars(content_type, length, count, shuffle=True):
    """

    :param content_type: 前五百“top_500”、中五百“middle_500”、后五百“last_500”或者前一千五“top_1500”
    :param length: 赛文长度
    :param count: 要多少篇
    :param shuffle: 是否乱序
    :return:
    """
    assert content_type in Chars.top_chars

    chars_dict = Chars.top_chars[content_type]
    chars = chars_dict['chars']  # 单字

    cycle_chars = cycle_str(chars, shuffle=shuffle)  # 无限迭代
    for _ in range(count):
        content = "".join((next(cycle_chars) for _ in range(length)))
        yield {
            "content": content,
            "title": chars_dict['title'] + ("-乱序" if shuffle else ""),
            "content_type": "单字",
        }


