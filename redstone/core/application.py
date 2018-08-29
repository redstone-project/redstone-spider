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

from .. import settings
from ..utils.log import logger
from ..utils.activemq import ActiveMQQueue


class RedstoneSpiderApplication(object):
    """
    代表整个爬虫App
    """
    def __init__(self):
        super(RedstoneSpiderApplication, self).__init__()

        # 普通爬虫任务队列
        self.normal_task_queue: ActiveMQQueue = None

        # chrome爬虫任务队列
        self.chrome_task_queue: ActiveMQQueue = None

        # 服务端的结果队列，用于传递爬取结果给服务端
        self.result_queue: ActiveMQQueue = None

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
            self.normal_task_queue = ActiveMQQueue(
                (settings.ACTIVEMQ_HOST, int(settings.ACTIVEMQ_PORT)),
                settings.ACTIVEMQ_USERNAME, settings.ACTIVEMQ_PASSWORD,
                settings.ACTIVEMQ_QUEUES.get("task_normal")
            )

            self.chrome_task_queue = ActiveMQQueue(
                (settings.ACTIVEMQ_HOST, int(settings.ACTIVEMQ_PORT)),
                settings.ACTIVEMQ_USERNAME, settings.ACTIVEMQ_PASSWORD,
                settings.ACTIVEMQ_QUEUES.get("task_chrome")
            )

            self.result_queue = ActiveMQQueue(
                (settings.ACTIVEMQ_HOST, int(settings.ACTIVEMQ_PORT)),
                settings.ACTIVEMQ_USERNAME, settings.ACTIVEMQ_PASSWORD,
                settings.ACTIVEMQ_QUEUES.get("result_spider")
            )

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