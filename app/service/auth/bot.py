# -*- coding: utf-8 -*-

"""
bot 的 ws api 验证相关
"""


def validate_access_token(token: str):
    """
    验证输入的 token 是否有效

    上线时，可以使用公钥机制，加密一个时间戳。
    这里就用私钥解密得到时间戳，在一定时限内，就认为有效。
    :param token:
    :return: boolean，是否有效
    """
    # TODO 待实现
    return True


