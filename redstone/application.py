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

import queue

from redstone import settings
from redstone.utils.log import logger
from redstone.utils.activemq import ActiveMQQueue
from redstone.core.loader import SpiderLoader
from redstone.core.engine.fetcher import FetcherEngine


class RedstoneSpiderApplication(object):
    """
    代表整个爬虫App
    """

    # 内部类，存储所有的Engine
    class AppEngines:
        WORKER_ENGINE: FetcherEngine = None
        # spider loader
        SPIDER_LOADER: SpiderLoader = None

    class BufferQueues:
        TASK_BUFFER_QUEUE: queue.Queue = None
        RESULT_BUFFER_QUEUE: queue.Queue = None

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

        # 初始化本地的buffer queue
        self.BufferQueues.TASK_BUFFER_QUEUE = queue.Queue(maxsize=settings.SPIDER_POOL_SIZE)
        self.BufferQueues.RESULT_BUFFER_QUEUE = queue.Queue()
        logger.info("Initialize local buffer queue success!")

        # 初始化爬虫加载器
        self.AppEngines.SPIDER_LOADER = SpiderLoader()
        self.AppEngines.SPIDER_LOADER.start()
        logger.info("Initialize spider_loader success!")

        # 初始化爬虫线程池


        return True
