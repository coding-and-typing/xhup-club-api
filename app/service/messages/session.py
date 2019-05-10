# -*- coding: utf-8 -*-
import json

from redis import Redis

from app import redis


class Session:
    def __init__(self, data, expires=180):
        """

        :param data: 当前消息的数据
        :param expires: 过期时间，以秒记
        """
        self.conn: Redis = redis.connection
        self.key = self.get_session_key(data)
        self.expires = expires

        self.context = self.conn.get(self.key)
        if not self.context:
            self.context = dict()

    @staticmethod
    def get_session_key(data):
        """会话"""
        m_type = data['message']['type']
        g_id = data["group"]['id'] if m_type == "group" else data['user']['id']
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

