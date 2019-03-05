"""
群成员权限验证
"""
from app import db
from app.models import Group


def _get_group(group_id, platform):
    return db.session.query(Group) \
        .filter_by(group_id=group_id, platform=platform) \
        .first()


def is_admin(main_user, group_id, platform):
    """
    该用户是否是指定群组的管理员
    需要用户先绑定群组！
    :param main_user: 用户对象
    :param group_id: 群组 id
    :param platform: 群组所属平台
    :return: boolean
    """
    group = _get_group(group_id, platform)

    # TODO 查询到 main_user 绑定的属于该群的账号

    # TODO 挨个检查各账号是否是 admin，是就返回 True

    return False


