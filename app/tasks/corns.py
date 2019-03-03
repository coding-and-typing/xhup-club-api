# -*- coding: utf-8 -*-
import logging
from app import rq

logger = logging.getLogger(__name__)

"""
定时任务，使用 rq.cron 实现
"""


# TODO 1. 通过 worker 异步发送邮件


# 定时任务，当前唯一的需求是，各个 QQ 群需要定时在北京时间 11:00 pm 或者  11:30 pm 收文章和成绩。
# 实现方法：启动时读取数据库中的定时任务表，使用 rq.corn 设置定时任务
#    任务启动时：
#           1. 在 redis 中为每个群设置一个 expire 为 60 秒的 flag（只针对需要响应的任务）
#           2. 同时向所有 bot 的 websocket 连接广播这个定时任务事件（名称叫 cron），消息还会自带 platform、group_id 参数
#               3. xhup-qq-bot 收到 platform 为 qq 的任务事件时，就将执行该任务。
#    然后这边收到小拆发送的文章或成绩图片时，flag 减去 1，当 flag 为 0 时，删除该 flag. （这样就不会出现图片或文章被保存多次的情况了）
