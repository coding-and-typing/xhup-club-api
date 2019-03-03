# -*- coding: utf-8 -*-
import logging
from app import rq

logger = logging.getLogger(__name__)

"""
定时任务，使用 rq.cron 实现

或者用 apscheduler？？？
"""
