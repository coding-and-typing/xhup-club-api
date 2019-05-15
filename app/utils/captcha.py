# -*- coding: utf-8 -*-
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
            return code


def generate_image_bytes(code: str, format: str):
    """生成验证码（图片）"""
    return image.generate(code, format=format).read()


def generate_captcha(seed: Optional[int] = None,
                     length: int = 4,
                     format: str = "png"):
    """生成验证码（先生成字符，再生成图片）"""
    code = generate_captcha_code(seed, length)

    return {
        "code": code,
        "image": generate_image_bytes(code, format=format),
        "format": format,
    }
