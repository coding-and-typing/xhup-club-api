# -*- coding: utf-8 -*-

"""
bot 的 ws api 验证相关
"""
from app import current_config


def validate_bot_token(token: str):
    """
    验证输入的 token 是否有效

    TODO 上线时，可以使用公钥机制，加密一个时间戳。
    这里就用私钥解密得到时间戳，在一定时限内，就认为有效。
    :param token:
    :return: boolean，是否有效
    """
    return token == current_config.BOT_TOKEN


