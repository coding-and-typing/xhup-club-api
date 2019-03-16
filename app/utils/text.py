# -*- coding: utf-8 -*-
from itertools import chain

import re
import random
import string

import chardet

"""
文字处理相关的工具函数
"""


class Chars:
    """字符相关"""

    # 1. 可以转换的全角字符，跟打前必须转换成半角
    # fl 是 full width （全宽）的缩写
    fl_ascii_lowercase = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
    fl_ascii_uppercase = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
    fl_ascii_letters = fl_ascii_lowercase + fl_ascii_uppercase
    fl_digits = "０１２３４５６７８９"

    # 全角与半角的对应表（不论是中文还是英文，都要使用此表做转换）
    fl_table = dict(zip(fl_ascii_letters + fl_digits,  # 全角
                        string.ascii_letters + string.digits))  # 半角

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
    }

    # 3. 中文文章文本替换，要使用的转换表
    table_all_cn = fl_table.update(punctuation_table)

    # 4. 处理完成后，中文文章允许包含的标点
    SYMBOLS_CN = frozenset("".join(punctuation_table.values())
                           + "、‘’“”{}《》〈〉〔〕|`@#￥%……&×——+-=·")  # 中英难以对应的标点（或者中英都使用同样的）

    # 5. 特殊字符中，可以转换成非特殊字符的
    SPECIAL_SPACE = "\u2001" + "\u200a" + "\u2009"  # 三个特殊空格
    SPECIAL_MIDDLE_LINE = "─—"

    # 6. 未做处理前，文章中允许出现的标点
    SYMBOLS_ALL = frozenset(chain(string.printable,
                                  SYMBOLS_CN,
                                  SPECIAL_SPACE,
                                  SPECIAL_MIDDLE_LINE))


def auto_decode(content: bytes):
    """检测编码，读取文件"""
    encoding = chardet.detect(content)['encoding']  # 检测编码

    return content.decode(encoding)


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
    text = text.translate(Chars.table_all_cn)

    # 引号成对转换
    # TODO 英文引号不分左右，不能这样直接替换
    # text = re.sub(r'"([^"]*)"', r"“\1”", text)
    # text = re.sub(r"'([^']*)'", r"‘\1’", text)

    # 破折号
    text = re.sub(rf"[{Chars.SPECIAL_MIDDLE_LINE}]+", "——", text)

    return text
