#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.spiders
    ~~~~~~~~~~~~~~~~

    爬虫的父类，所有的爬虫都要继承这个类

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""
from typing import List, Dict

import requests

from redstone import settings
from redstone.utils.log import logger


class SpiderBase(object):
    """
    爬虫的基类，所有的爬虫都需要继承这个类
    这个类中提供了一些基础方法，在编写爬虫的时候可以直接使用
    """

    def __init__(self):
        super(SpiderBase, self).__init__()

        # 存储结果的list
        # self._results: List[Dict[str, str]] = []

        # 存储待爬取的URL
        self._url: str = None

        # 配置文件
        # {
        #   "use_proxy": True/False
        # }
        self._config: Dict[str, str] = None

        # 存储爬虫结果的类
        self.spider_result = {
            # 爬虫是否运行成功
            "success": False,

            # 错误消息，如果正常运行，则为空
            "error_message": "",

            # 错误stack消息，如果正常运行，则为空
            "error_stack_info": "",

            # items列表
            "results": [],  # type: List[Dict[str, str]]
        }

    def run(self):
        """
        引擎调用
        需要子类重写该方法，爬虫的主线程
        """
        pass

    def get_result(self):
        """
        引擎调用，获取爬虫的结果
        """
        return self.spider_result

    def set_params(self, url, config):
        self._url = url
        self._config = config

    def _push_result(self, result: Dict):
        """
        爬虫调用
        将一个爬取结果放到结果集中
        :param result: 爬取的结果item
        """
        self.spider_result["results"].append(result)

    def _get_page_content(self, url=None):
        """
        爬虫调用
        获取指定URL的页面内容，如果没有指定URL，则使用self._url
        :param url: 待爬取的URL
        """

        ret_val = {
            "success": False,
            "message": "error message!",
            "page_content": ""
        }

        target_url = url if url else self._url

        try:
            # todo: add socks5 proxy support
            if self._config["use_proxy"]:
                resp = requests.get(target_url, timeout=(30, 30), proxies=settings.SPIDER_PROXIES)
            else:
                resp = requests.get(target_url, timeout=(30, 30))
        except requests.exceptions.RequestException as e:
            ret_val["success"] = False
            ret_val["message"] = "Error when make requests. Error: {}".format(e)
            logger.error(ret_val["message"])
            return ret_val

        if resp.status_code != 200:
            ret_val["success"] = False
            ret_val["message"] = "Target URL: {} return status_code: {}".format(target_url, resp.status_code)
            logger.error(ret_val["message"])
            return ret_val

        # text is unicode type, reps.content is bytes
        # use text instead
        content = resp.text

        ret_val["success"] = True
        ret_val["message"] = "success"
        ret_val["page_content"] = content
        logger.debug("Get page content success!")
        return ret_val
