# -*- coding: utf-8 -*-
import json
import re
from io import StringIO
from operator import itemgetter
from pkg_resources import parse_version

from app import db
from app.models import Group
from app.models.character import Character, CharsTable

"""
小鹤音形 - 拆字表查询
"""

# Unicode 中日韩统一汉字区（不包括补充字符集）
# 参考 https://zh.wikipedia.org/wiki/Unicode#%E6%BC%A2%E5%AD%97%E5%95%8F%E9%A1%8C
cjk_re = "[\u4e00-\u9fbb]"


class XHUP(object):
    """小鹤音形词条的解析类"""

    @staticmethod
    def parse_table(table: str, table_id: int):
        """解析小鹤音形拆字表"""
        table_io = StringIO(table)
        for line in table_io:
            yield XHUP.parse_line(line.strip(), table_id)

    @staticmethod
    def parse_line(line: str, table_id: int):
        line = re.sub(r"[ 　]+", " ", line)  # 中文空格与英文空格，连带出现
        char = line[0]
        parts = line.split("=")
        codes = parts[0].replace(f"{char}： ", "")
        split = parts[1].replace(f"拆分： ", "")
        otehr_info = json.dumps(
            dict(pair.split("： ") for pair in parts[2:]))
        return Character(char=char,
                         codes=codes,
                         split=split,
                         other_info=otehr_info,
                         table_id=table_id)


# 针对不同的编码表，调用不同的 parser
parsers = {
    "xhup": XHUP
}


def save_split_table(table: str,
                     version: str,
                     table_type: str,
                     table_name: str,
                     group_id: str,
                     platform: str):
    """

    :param table: 待解析的拆字表字符串
    :param version: 拆字表版本号
    :param table_type: 编码表类型，用于确定应该调用的解析器
    :param table_name: 编码表名称（如小鹤音形拆字表）
    :param group_id: 群组 id（非数据库 id）
    :param platform: 该群所属平台
    :return:
    """
    version_ = parse_version(version)

    if version_ <= get_latest_version(table_name):
        raise RuntimeError("the version has existed!")

    # 新建 version 行
    group_db_id = db.session.query(Group) \
        .filter_by(group_id=group_id, platform=platform) \
        .first().id
    chars_table = CharsTable(name=table_name,
                             version=version,
                             group_db_id=group_db_id)
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

    return {
        "version": version,
        "table_name": table_name,
        "group_id": group_id,
        "platform": platform,
    }


def get_latest_version(table_name: str):
    """获取最新的拆字表版本号"""
    versions = map(itemgetter(0), db.session.query(CharsTable.version) \
                   .filter_by(name=table_name))
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
    info: Character = db.session.query(Character) \
        .filter_by(char=char, table_id=table_id) \
        .first()

    info.other_info = json.loads(info.other_info)
    return info
