# -*- coding: utf-8 -*-
from io import StringIO
from operator import itemgetter
from pkg_resources import parse_version

from app import db
from app.models.characters import Character

"""
小鹤音形 - 拆字表查询
"""


def save_split_table(table: str, version: str):
    """

    拆分条目格式：[比：　bi bibb*=拆分：　比左 匕=首末：　比左 匕=编码：　b  b]
    :param table: 待解析的拆字表字符串
    :param version: 拆字表版本号
    :return: 
    """
    version = parse_version(version)  # version 错误会抛异常！

    if version <= get_latest_version():
        raise RuntimeError("版本号必须大于当前最新的版本号")

    table_io = StringIO(table)
    for line in table_io:
        char = Character(char=line[0], info=line, version=version)
        db.session.add(char)

    db.session.commit()


def get_latest_version():
    """获取最新的拆字表版本号"""
    versions = map(itemgetter(0), db.session.query(Character.version))
    versions = map(parse_version, versions)
    latest_version = max(versions)

    return latest_version


def get_info(char: str, version=None):
    if not version:
        version = str(get_latest_version())
    info = db.session.query(Character.info) \
        .filter_by(char=char, version=version) \
        .first()

    return info[0] if info else None


