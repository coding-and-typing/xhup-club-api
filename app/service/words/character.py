# -*- coding: utf-8 -*-
from io import StringIO
from operator import itemgetter
from pkg_resources import parse_version

from app import db
from app.models import Group
from app.models.character import Character, CharsTable

"""
小鹤音形 - 拆字表查询
"""


class XHUP(object):
    """小鹤音形词条的解析类"""
    @staticmethod
    def parse_table(table: str, table_id: int):
        """解析小鹤音形拆字表"""
        table_io = StringIO(table)
        for line in table_io:
            yield XHUP.parse_line(line, table_id)

    @staticmethod
    def parse_line(line: str, table_id: int):
        pass


# 针对不同的编码表，调用不同的 parser
parsers = {
    "xhup": XHUP
}


def save_split_table(table: str,
                     version: str,
                     table_type: str, # 编码表类型，用于确定应该调用的解析器
                     table_name: str,  # 编码表名称（如小鹤音形拆字表）
                     group_id: str,  # 群组 id（非数据库 id）
                     group_platform: str):  # 该群所属平台
    """

    :param table: 待解析的拆字表字符串
    :param version: 拆字表版本号
    :return:
    """
    version_ = parse_version(version)  # version 错误会抛异常！

    if version_ <= get_latest_version(table_name):
        raise RuntimeError("the version has existed!")

    # 新建 version 行
    group_db_id = db.session.query(Group) \
        .filter_by(group_id=group_id, platform=group_platform) \
        .first().id
    chars_table = CharsTable(name=table_name,
                             version=version,
                             group_id=group_db_id)
    db.session.add(chars_table)  # 将 chars_table 插入表中
    table_id = db.session.query(CharsTable) \
        .filter_by(name=table_name, version=version) \
        .first().id

    # 解析拆字表
    parser = parsers[table_type]
    for char in parser.parse_table(table, table_id):  # 批量插入
        db.session.add(char)

    # 最后提交修改
    db.session.commit()


def get_latest_version(table_name: str):
    """获取最新的拆字表版本号"""
    versions = map(itemgetter(0), db.session.query(CharsTable.version) \
                   .filer_by(name=table_name))
    versions = list(map(parse_version, versions))
    latest_version = max(versions) if versions else parse_version("0.0.0")

    return latest_version


def get_info(char: str, table_name, version=None):
    if not version:
        version = str(get_latest_version(table_name))

    # 通过 version 查找拆字表 id
    table_id = db.session.query(CharsTable.id) \
        .filter_by(version=version).first()[0]

    # 在该拆字表内查找 char 的信息
    info = db.session.query(Character) \
        .filter_by(char=char, table_id=table_id) \
        .first()

    return info


