# -*- coding: utf-8 -*-
from uuid import uuid4

import random
import string
from captcha.image import ImageCaptcha
from typing import Optional

from app import current_config, redis

chars = string.digits + string.ascii_letters

image = ImageCaptcha(fonts=current_config.FONTS_PATH)


def generate_captcha_code(seed: int = None, length: int = 4):
    """生成验证码（字符）"""
    if seed:
        random.seed(seed)
    while True:
        code = "".join(random.choices(chars, k=length))
        if not redis.connection.exist(code):  # 保证唯一性
            # (多线程下，不能保证这里的 check 与后面的 insert 的原子性，可能会出错)
            return code


def generate_image_bytes(code: str, format: str):
    """生成验证码（图片）"""
    return image.generate(code, format=format).read()


def generate_captcha(seed: Optional[int] = None,
                     length: int = 4,
                     format: str = "png"):
    """生成验证码（先生成字符，再生成图片）"""
    code = generate_captcha_code(seed, length)
    capthca_key = uuid4()  # 理论上有碰撞的可能，但验证码嘛，换一个就是了。

    key = current_config.CAPTCHA_FORMAT.format(capthca_key)
    redis.connection.set(key, code,   # 验证码存入 redis
                         ex=current_config.VERIFICATION_CODE_EXPIRES)
    return {
        "key": key,
        "code": code,
        "image": generate_image_bytes(code, format=format),
        "format": format,
    }
