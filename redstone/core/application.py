#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.core.application
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    爬虫模块的核心类，该类代表整个爬虫模块App

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""

import stomp

from .. import settings
from ..utils.log import logger


class RedstoneSpiderApplication(object):
    """
    代表整个爬虫App
    """
    def __init__(self):
        super(RedstoneSpiderApplication, self).__init__()

        # 服务端的任务队列，用于获取爬虫任务
        self.task_queue: stomp.StompConnection11 = None

        # 服务端的结果队列，用于传递爬取结果给服务端
        self.result_queue: stomp.StompConnection11 = None

        # 普通的爬虫引擎
        self.normal_spider_engine = None

        # 基于chrome headless的爬虫引擎
        self.chrome_spider_engine = None

    def __connect_queue(self):
        """
        连接到服务端的任务队列和结果队列
        :return: True-连接成功，False-连接失败
        :type: bool
        """
        try:
            # 连接任务队列
            self.task_queue = stomp.Connection([(settings.ACTIVEMQ_HOST, int(settings.ACTIVEMQ_PORT))])
            self.task_queue.start()
            self.task_queue.connect(settings.ACTIVEMQ_USERNAME, settings.ACTIVEMQ_PASSWORD, wait=True)

            # 连接结果队列
            self.result_queue = stomp.Connection([(settings.ACTIVEMQ_HOST, int(settings.ACTIVEMQ_PORT))])
            self.result_queue.start()
            self.result_queue.connect(settings.ACTIVEMQ_USERNAME, settings.ACTIVEMQ_PASSWORD, wait=True)

            logger.info("Connect to remote ActiveMQ queue success!")
            return True
        except Exception as e:
            logger.error("Error when connect to remote ActiveMQ queue! Error: {}".format(e))
            return False

    def start(self) -> bool:
        """
        启动方法，负责启动整个爬虫模块
        :return: True-启动成功，False-启动失败
        :rtype: bool
        """
        # 连接到远程队列
        if not self.__connect_queue():
            return False

        # 初始化爬虫线程池


        return True
