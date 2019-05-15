# -*- coding: utf-8 -*-
import json

from redis import Redis

from app import redis


class Session:
    def __init__(self, data, expires=1800):
        """

        :param data: 当前消息的数据
        :param expires: 过期时间，以秒记
        """
        self.conn: Redis = redis.connection
        self.key = self.get_session_key(data)
        self.expires = expires

        context = self.conn.get(self.key)
        self.context = json.loads(context) if context else dict()
        if not self.context:
            self.context = dict()

    @staticmethod
    def get_session_key(data):
        """会话"""
        message = data['message']
        m_type = message['type']
        g_id = message["group"]['id'] if m_type == "group" else message['user']['id']
        key = f"{data['platform']}:{m_type}:{g_id}"  # e.g. qq:group:group_id, qq:private:user_id

        return key

    def get(self, k):
        return self.context.get(k)

    def set(self, k, v, flush=True):
        self.context[k] = v

        if flush:  # 立即将修改写入 redis
            self.flush()

    def flush(self):
        """将 session 写入 redis"""
        v = json.dumps(self.context)
        self.conn.set(self.key, v, ex=self.expires)

    def destroy(self):
        """销毁当前 session"""
        self.conn.delete(self.key)
