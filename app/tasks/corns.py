# -*- coding: utf-8 -*-
import logging

import rq

logger = logging.getLogger(__name__)

"""
定时任务，使用 rq.cron 实现
"""
