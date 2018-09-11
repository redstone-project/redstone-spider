#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.spiders.rss
    ~~~~~~~~~~~~~~~~~~~~

    RSS 爬虫模块

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""
import time

import feedparser

from redstone.utils.log import logger
from . import SpiderBase


class RSSSpider(SpiderBase):

    def run(self):
        logger.info("RSS Spider running, target: {}".format(self._url))

        # 获取RSS页面的内容
        resp_result = self._get_page_content()
        if not resp_result["success"]:
            logger.error("Can't fetch target URL, error msg: {}".format(resp_result["message"]))
            return False

        # 解析RSS
        raw_rss_content = resp_result["page_content"]
        parsed_rss = feedparser.parse(raw_rss_content)

        # 提取item信息，最后封装成一个dict
        """
        item = {
            "title": "",
            "link": "",
            "summary": ""
            "content": "" if not empty else title+url,
            "publish_time": "",
        }
        """
        items = parsed_rss["entries"]
        # rss_info = parsed_rss["feed"]

        for item in items:
            title = item["title"]
            link = item["link"]
            summary = item["summary"] if item["summary"] else "该文章暂无简介"
            content = item["content"]
            if not content:
                content = "{title}<br><a href=\"{link}\">{title}</a>".format(title=title, link=link)

            # 处理时区问题
            raw_published_time = item["published"]
            fmt1 = "%a, %d %b %Y %H:%M:%S %z"
            fmt2 = "%a, %d %b %Y %H:%M:%S %Z"
            try:
                st = time.strptime(raw_published_time, fmt1)
            except ValueError:
                try:
                    st = time.strptime(raw_published_time, fmt2)
                except ValueError:
                    # 没救了，转不出来
                    logger.warning(
                        "Can't convert rss time to struct_time: '{}', use current time instead.".format(
                            raw_published_time))
                    st = time.localtime()

            # 把struct_time转成timestamp
            published_time = time.mktime(st)

            # 拼装result
            result = {
                "title": title,
                "link": link,
                "summary": summary,
                "content": content,
                "publish_time": published_time
            }
            self._push_result(result)

        logger.info("Rss spider done.")


def get_class():
    return RSSSpider
