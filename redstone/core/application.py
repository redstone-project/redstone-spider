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

from __future__ import annotations

from ..utils.log import logger
from ..utils.activemq import ActiveMQQueue
from redstone.core.engine.fetcher import ThreadFetchAgent


class RedstoneSpiderApplication(object):
    """
    代表整个爬虫App
    """

    # 内部类，存储所有的Engine
    class AppEngines:
        # 基于线程的FetchAgent
        THREAD_FETCH_AGENT: ThreadFetchAgent = None

    def exit_signal_func(self):
        pass

    def __init__(self):
        super(RedstoneSpiderApplication, self).__init__()

        # 服务端的结果队列，用于传递爬取结果给服务端
        self.result_queue: ActiveMQQueue = None

        # todo: set ctrl+c signal

    def start(self) -> bool:
        """
        启动方法，负责启动整个爬虫模块
        :return: True-启动成功，False-启动失败
        :rtype: bool
        """

        logger.info("Starting RedstoneSpiderApplication!")

        # 初始化爬虫线程池
        self.AppEngines.THREAD_FETCH_AGENT = ThreadFetchAgent()
        self.AppEngines.THREAD_FETCH_AGENT.start()

        return True
