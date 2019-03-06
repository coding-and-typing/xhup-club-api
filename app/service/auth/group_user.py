"""
群成员权限验证
"""
from typing import Iterable, List

from app import db
from app.models import Group, GroupUser, MainUser, GroupUserRelation


def _get_group(group_id, platform):
    return db.session.query(Group) \
        .filter_by(group_id=group_id, platform=platform) \
        .first()


def is_(role: List[str], main_user: MainUser, group_id, platform):
    """
    该用户是否是指定群组的管理员
    需要用户先绑定群组！
    :param role: 群角色，可选 'admin' 或 'owner'，可多选
    :param main_user: 用户对象
    :param group_id: 群组 id
    :param platform: 群组所属平台
    :return: boolean
    """
    group = _get_group(group_id, platform)

    # 查询到 main_user 绑定的属于该群的账号
    group_users_id: Iterable[GroupUser.id] = db.session.query(GroupUser.id) \
        .filter_by(platform=platform, main_user_id=main_user.id)

    group_user_relationship: Iterable[GroupUserRelation] = db.session.query(GroupUserRelation) \
        .filter_by(platform=platform, group_db_id=group.id) \
        .filter(GroupUserRelation.user_db_id.in_(group_users_id))

    # 挨个检查各账号是否是 admin，是就返回 True
    for r in group_user_relationship:
        if 'admin' in role and r.is_admin:
            return True
        elif 'owner' in role and r.is_owner:
            return True

    return False



