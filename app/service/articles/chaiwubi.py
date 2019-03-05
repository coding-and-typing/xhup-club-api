# -*- coding: utf-8 -*-
from collections import defaultdict

from datetime import datetime, date, timedelta

import logging
import requests
from bs4 import BeautifulSoup
from requests.cookies import cookiejar_from_dict
from urllib import parse
from urllib.parse import SplitResult

from app import current_config

logger = logging.getLogger(__name__)

"""
与小拆赛文录入系统的交互模块

TODO 暂时是直接 copy 自曾经的赛文批量添加工具
实际使用时还需要修改！
"""


class ArticleAdder(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.session = requests.session()
        url: SplitResult = parse.urlsplit(current_config.CHAIWUBI_URL)
        self.session.headers = {
            "User-Agent": current_config.USER_AGENT,
            "Host": url.netloc,
            "Origin": parse.urlunsplit((url.scheme, url.hostname, *('',)*3)),
        }

        # 先获取一下 cookie
        self.session.get(current_config.CHAIWUBI_URL)

    def login(self):
        """
        登录
        :return: dict
            success 为是否成功的 bool 值
            message 为返回的消息
        """
        data = {
            "matchuser": self.username,
            "matchpass": self.password  # 是的，是 http 明文密码emmm
        }

        resp = self.session.post(current_config.CHAIWUBI_API, data=data)
        resp_json = resp.json()

        if int(resp_json['code']) != 200:
            logger.info(f"登录异常，msg: {resp_json['msg']}")
            return {
                "success": False,
                "message": resp_json['msg']
            }

        logger.info("登录成功")
        self.session.cookies = cookiejar_from_dict({"matchuser": self.username})  # cookie 是通过 js 设置的，直接用的用户名。。。
        return {
            "success": True,
            "message": resp_json['msg']
        }

    def get_info(self, entries_index="list"):
        """
        获取最新的已添加赛文信息
        :type entries_index: str
        :param entries_index: entries 的索引方式，默认为 list
        :return: dict
            groups 与当前账号相关联的 QQ 群 的列表
            entries 未开始的所有赛文的 dict
        """

        def _get_entries(tb: BeautifulSoup):
            entries = []
            for tr in tb.find_all("tr", attrs={"data-tid": True}):
                tds: list = tr.find_all("td")

                # 日期解析
                date_ = datetime.strptime(tds[4].getText(), "%Y-%m-%d %H:%M:%S").date()
                entries.append({
                    "id": int(tr.get("data-tid")[2:]),
                    "title": tds[1].getText(),
                    "number": tds[3].getText(),
                    "date": date_,
                })
            return entries

        def get_entries(tb: BeautifulSoup, index_type):
            """获取文章条目，同时转换索引方式"""
            entries = _get_entries(tb)

            if index_type == "list":
                return entries
            else:
                res = defaultdict(list)

                for entry in entries:
                    res[entry[str(index_type)]].append(entry)

                return res

        resp = self.session.get(current_config.CHAIWUBI_URL)
        bsObj = BeautifulSoup(resp.text, "html.parser")

        # 获取未结束的赛文
        table = bsObj.find("table", attrs={"class": "match-sh"})
        entries = get_entries(table, entries_index)

        # 获取账号绑定的QQ群信息
        groups = [
            {
                "group_id": int(option.get("value")),
                "group_name": option.getText()
            }
            for option in bsObj.find_all("option")]

        return {
            "groups": groups,
            "entries": entries
        }

    def add_article(self, content: str,
                    start_datetime: datetime,
                    end_datetime: datetime,
                    group_id, number, title, subtitle, producer, content_type,
                    swid: int = 0,
                    level: int = 3):
        """
        添加赛文，其实就是把文章参数组装一下，直接post上去

        :param 所有参数的含义见下面的注释
        :return:
        """

        article_dict = {
            "swid": swid,  # 赛文 id，为 0 时表示新增赛文。为已存在的赛文 id 时表示修改赛文
            "m_gid": group_id,  # 群号
            "m_qishu": number,  # 赛文期数
            "m_title": f"《{title}》",  # 赛文标题
            "m_subtitle": subtitle,  # 子标题：日赛、周赛等
            "m_chutiren": producer,  # 赛文制作人
            "m_zucheng": content_type,  # 赛文内容：单字、散文等
            "m_clock": 1200,  # 赛文跟打时间，好像没啥用
            "m_nandu": level,  # 难度
            "m_kaishi": start_datetime.strftime("%Y-%m-%d %H:%M"),  # 开始时间，不能晚于当前时间  "2018-09-07 11:24"
            "m_jieshu": end_datetime.strftime("%Y-%m-%d %H:%M"),  # 结束时间
            "m_content": content  # 赛文内容
        }

        resp_json = self.session.post(current_config.CHAIWUBI_API, data=article_dict).json()

        return {
            "success": int(resp_json['code']) == 200,
            "message": resp_json['msg']
        }

    def edit_article_by_swid(self,
                             swid,
                             func=None,
                             **kwargs):
        """
        修改已添加赛文
        :param swid: 需要修改的赛文的id
        :param func: 用于修改的函数，用于对 content 做小修改
        :param kwargs: 其它参数，见下
        :return: 成功与否，还有附加信息
        """
        resp = self.session.post(current_config.CHAIWUBI_API, data={
            "action": "edit",
            "id": swid
        })
        article_raw = resp.json()['msg']

        logger.info(f"正在修改赛文：{article_raw['gm_title']} - {article_raw['gm_subtitle']} 第{article_raw['gm_qishu']}期")

        payload = {
            "swid": swid,  # 赛文 id，为 0 时表示新增赛文。为已存在的赛文 id 时表示修改赛文
            "m_gid": kwargs.get("group_id", article_raw['gm_gid']),  # 群号
            "m_qishu": kwargs.get("number", article_raw['gm_qishu']),  # 赛文期数
            "m_title": kwargs.get("title", article_raw['gm_title']),  # 赛文标题
            "m_subtitle": kwargs.get("subtitle", article_raw['gm_subtitle']),  # 子标题：日赛、周赛等
            "m_chutiren": kwargs.get("producer", article_raw['gm_chutiren']),  # 赛文制作人
            "m_zucheng": kwargs.get("content_type", article_raw['gm_zucheng']),  # 赛文内容：单字、散文等
            "m_clock": article_raw['gm_clock'],  # 赛文跟打时间，好像没啥用
            "m_nandu": kwargs.get("level", article_raw['gm_nandu']),  # 难度
            "m_kaishi": kwargs.get("start_datetime", article_raw['gm_kaishi']),  # 开始时间，不能晚于当前时间  "2018-09-07 11:24"
            "m_jieshu": kwargs.get("end_datetime", article_raw['gm_jieshu']),  # 结束时间
            "m_content": kwargs.get("content", article_raw['gm_content'])  # 赛文内容
        }

        # 使用 func 做高级修改
        if func is not None:
            payload = func(payload)

        resp_json = self.session.post(current_config.CHAIWUBI_API, data=payload).json()

        return {
            "success": int(resp_json['code']) == 200,
            "message": resp_json['msg']
        }

    def delete_article(self, swid):
        """通过给定的赛文id删除赛文"""
        resp = self.session.post(current_config.CHAIWUBI_API, data={
            "action": "del",
            "id": swid
        })
        resp_json = resp.json()

        return {
            "success": resp_json['code'] == 200,
            "message": resp_json['msg']
        }

    def delete_article_by_date(self,
                               date_start: date,
                               date_end: date,
                               date_step: timedelta = timedelta(days=1),
                               info: dict = None):
        """
        批量删除指定日期区段的赛文，赛文添加出现问题时常用
        :param date_start: 要删除的赛文的起始日期
        :param date_end: 删除到这个日期为止
        :param date_step: 日期间隔，每隔这么长时间删除一篇文章
        :param info: get_info 的返回值，会根据这个信息执行删除操作。
                    务必使用最新的 info（默认是每次删除时自动获取）
        :return: None
        """
        if not info:
            info = self.get_info(entries_index="date")  # 自动获取最新 info，使用日期索引entries

        # 赛文条目
        entries = info["entries"]

        date_tmp = date_start
        while date_tmp <= date_end:
            for entry in entries[str(date_tmp)]:
                self.delete_article(entry['id'])

                logger.info(f"已删除 {entry['title']} - 第{entry['number']}期，赛文日期 {str(date_tmp)}")

            date_tmp += date_step

    def delete_article_by_number(self,
                                 number_start: int,
                                 number_end: int,
                                 number_step: int = 1,
                                 info: dict = None):
        """
        通过指定赛文期数范围来删除赛文
        :param number_start: 要删除的赛文，期数起始点
        :param number_end: 期数的结束点
        :param number_step: 间隔
        :param info: get_info 的返回值，会根据这个信息执行删除操作。
                    务必使用最新的 info（默认是每次删除时自动获取）
        :return: None
        """
        if not info:
            info = self.get_info(entries_index="list")  # 自动获取最新 info，使用日期索引entries

        # 赛文条目
        entries = info["entries"]

        numbers = list(range(number_start, number_end + 1, number_step))
        for entry in entries:
            if int(entry['number']) in numbers:
                self.delete_article(entry['id'])
                logger.info(f"已删除 {entry['title']} - 第{entry['number']}期，赛文日期 {entry['date']}")

    def add_articles(self, articles: list,
                     start_number: int,
                     start_datetime: datetime,
                     end_datetime: datetime,
                     date_step: timedelta = timedelta(days=1),
                     **kwargs):
        """批量添加赛文
            articles  赛文 list，内部是 dict
            start_number 批量赛文的起始期数
            start_datetime 赛文开始的时间
            end_datetime  赛文结束时间
            """
        # 上传文章
        for i, article in enumerate(articles):
            number = start_number + i
            start = start_datetime + date_step * i
            end = end_datetime + date_step * i
            state, message = self.add_article(**article,
                                              number=number,
                                              start_datetime=start,
                                              end_datetime=end,
                                              **kwargs)

            if state:
                logger.info(f"添加成功，期数: {number}")
            else:
                logger.error(f"添加异常，期数: {number}，消息：{message}")


