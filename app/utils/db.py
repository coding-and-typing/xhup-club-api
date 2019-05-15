# -*- coding: utf-8 -*-
from app import db
from app.models import Group, GroupUser, GroupUserRelation

"""与数据库相关的一些实用函数"""


def get_group(group_id, platform):
    return db.session.query(Group) \
        .filter_by(group_id=group_id, platform=platform) \
        .first()


def get_or_insert_group(platform, group_id, group_name):
    while True:
        group = get_group(group_id, platform)
        if not group:  # 不存在，就新建
            group = Group(platform=platform, group_id=group_id, group_name=group_name)
            db.session.add(group)
            db.session.commit()
        else:
            return group


def get_group_user(group_user_id, platform):
    return db.session.query(GroupUser) \
        .filter_by(user_id=group_user_id, platform=platform) \
        .first()


def get_or_insert_group_user(platform, group_user_id, group_username, mainuser):
    while True:
        group_user = get_group_user(group_user_id, platform)
        if not group_user:  # 不存在
            group_user = GroupUser(platform=platform,
                                   user_id=group_user_id,
                                   username=group_username,
                                   main_user_id=mainuser.id)
            db.session.add(group_user)
            db.session.commit()
        else:
            return group_user


def insert_group_user_relation(platform, group_db_id, user_db_id, is_admin, is_owner):
    relation_old = db.session.query(GroupUserRelation)\
        .filter_by(platform=platform, group_db_id=group_db_id, user_db_id=user_db_id).first()
    if relation_old is not None:  # 该关系已经存在
        db.session.update(platform=platform,
                          group_db_id=group_db_id,
                          user_db_id=user_db_id,
                          is_admin=is_admin,
                          is_owner=is_owner)
        db.session.commit()
        return "绑定信息更新成功！"
    else:  # 添加新关系
        relation = GroupUserRelation(platform=platform,
                                     group_db_id=group_db_id,
                                     user_db_id=user_db_id,
                                     is_admin=is_admin,
                                     is_owner=is_owner)
        db.session.add(relation)
        db.session.commit()
        return "绑定完成！"



