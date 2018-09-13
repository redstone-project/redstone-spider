#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.core.engine.worker.worker
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    爬虫engine

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""
import sys
import traceback
import json
import queue
import threading
from typing import TYPE_CHECKING, Optional

from redstone.spiders import SpiderBase
from redstone.utils.log import logger
from ..base import MultiThreadBaseEngine


if TYPE_CHECKING:
    from redstone.application import RedstoneSpiderApplication


class SpiderWorkerEngine(MultiThreadBaseEngine):

    def __init__(self, app_ctx):
        super(SpiderWorkerEngine, self).__init__()

        # engine 名称
        self.name = "SpiderWorkerEngine"

        # 工作线程
        self.thread: threading.Thread = None

        # Running Status, Event Flag
        self.status = self.EngineStatus.STATUS_RUNNING
        self.ev = threading.Event()

        # Redstone App Context
        self.app_context: RedstoneSpiderApplication = app_ctx

    def _worker(self):
        """
        从local buffer queue中接收任务，执行，并且存到result local buffer queue中
        """

        task_queue = self.app_context.BufferQueues.TASK_BUFFER_QUEUE
        result_queue = self.app_context.BufferQueues.RESULT_BUFFER_QUEUE
        spider_loader = self.app_context.AppEngines.SPIDER_LOADER

        while self.status == self.EngineStatus.STATUS_RUNNING:
            try:
                message = task_queue.get_nowait()
            except queue.Empty:
                self.ev.wait(1)
                continue
            """
            task = {
                "feed_url": "url",
                "feed_id": 123,
                "feed_name": "name",
                "feed_config": {
                    "use_proxy": True,
                    # ...other config
                },
                "spider_name": "SpiderName"
            }
            
            SpiderName: ExampleSpider 
                => Pkg name: example_spider 
                => Filename: example_spider.py
            """
            task = json.loads(message)
            feed_url = message["feed_url"]
            feed_name = message["feed_name"]
            feed_id = message["feed_id"]
            feed_config = message["feed_config"]  # 该feed的额外设置，例如use_proxy等
            spider_name = message["spider_name"]  # use this to load spider class

            # 加载爬虫类 并实例化
            spider_cls: Optional[SpiderBase] = spider_loader.load_class_by_name(spider_name)
            if spider_cls is None:
                return False
            # PyCharm并不能检测到我在实例化一个对象，它认为我在调用一个函数
            spider_instance: SpiderBase = spider_cls()

            # 设置爬虫运行所需要的数据
            spider_instance.set_params(url=feed_url, config=feed_config)

            # 运行爬虫，这里同步等待爬虫结束
            logger.debug("Before spider run..")
            try:
                spider_instance.run()
            except Exception as e:
                exc_type, exc_value, exc_tb = sys.exc_info()
                tbe = traceback.TracebackException(exc_type, exc_value, exc_tb)
                full_err = ''.join(tbe.format())
                logger.fatal("Oops! Error when spider running! Error: {}".format(e))
                logger.fatal("Full error below: \n{}".format(full_err))
                continue
            logger.debug("After spider run..")

            # 获取爬虫结果
            result = spider_instance.get_result()

            # 基本上不会满，直接put即可
            result_queue.put(result)
