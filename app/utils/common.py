# -*- coding: utf-8 -*-

"""
实用函数
"""
import time
from itertools import chain, zip_longest

from flask_login import login_required as login_required_
from flask_smorest.utils import deepupdate
from operator import truth


def login_required(func):
    """包装 flask-login 的 login_required 装饰器
    给该函数的 401 响应添加 api doc
    """

    doc = {'responses': {"401": {'description': "需要先登录，才能调用此 api"}}}
    func._api_manual_doc = deepupdate(getattr(func, '_api_manual_doc', {}), doc)

    return login_required_(func)


def timestamp():
    """Return the current timestamp as an integer."""
    return int(time.time())


def group_each(a, size: int, allow_none=False):
    """
        将一个可迭代对象 a 内的元素, 每 size 个分为一组
        group_each([1,2,3,4], 2) -> [(1,2), (3,4)]
    """
    func = zip_longest if allow_none else zip

    iterators = [iter(a)] * size  # 将新构造的 iterator 复制 size 次（浅复制）
    return func(*iterators)  # 然后 zip


def iter_one_by_one(items, allow_none=False):
    func = zip_longest if allow_none else zip

    return chain.from_iterable(func(*items))


def filter_truth(items):
    return filter(truth, items)  # 过滤掉判断为 False 的 items


def equal(a, b):
    """判断两个 object 的内容是否一致（只判断浅层数据）"""
    return a.__dict__ == b.__dict__
