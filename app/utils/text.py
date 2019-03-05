# -*- coding: utf-8 -*-
import random

import chardet
import re

from app import current_config

"""
文字处理相关的工具函数
"""


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
    special_space = ''.join([r'　', r" ", r' '])
    return re.sub(rf"[\s{special_space}]", "", s)


def sub_punctuation(text: str):
    """
    将文本中的半角标点转换成全角标点
    :param text: 文本
    :return: 转换后的文本
    """
    text = text.translate(current_config.PUNCTUATIONS_TABLE)

    # 引号成对转换
    # TODO 英文引号不分左右，不能这样直接替换
    # text = re.sub(r'"([^"]*)"', r"“\1”", text)
    # text = re.sub(r"'([^']*)'", r"‘\1’", text)

    # 破折号
    text = re.sub(r"[-─—]+", "——", text)

    return text
