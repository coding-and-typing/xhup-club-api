# -*- coding: utf-8 -*-
from dotenv import load_dotenv
from pathlib import Path

# 导入之前，先加载环境变量
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)


from .base import *
from .dev import *
from .test import *
from .prod import *

"""
配置文件
"""

config_by_name = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig
}