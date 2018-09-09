#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.core.engine.sender.sender
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    sender 模块，将爬取的结果从本地的buffer queue中发回result queue

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""
import queue
import threading
from typing import Dict

from redstone.core.engine.base import SingleThreadBaseEngine
from redstone.utils.activemq import ActiveMQQueue
from redstone.utils.log import logger
from redstone.utils.common import make_consumer_id


class SenderEngine(SingleThreadBaseEngine):
    """
    Sender Engine, 将爬虫结果发回远程服务端
    """

    def __init__(self, queue_info: Dict[str, str]):
        super(SenderEngine, self).__init__()

        # engine 名称
        self.name = "SendEngine"

        # 工作线程
        self.thread: threading.Thread = None

        # Running Status, Event flag
        self.status = self.EngineStatus.STATUS_RUNNING
        self.ev = threading.Event()

        # 远端的结果队列
        self.remote_result_queue: ActiveMQQueue = None
        self.queue_info: Dict[str, str] = queue_info

    def __connect_remote_queue(self):
        """
        连接到远程的ActiveMQ队列
        :return: True-连接成功，False-连接失败
        :rtype: bool
        """
        queue_info = self.queue_info
        check_key = ("host", "port", "username", "password", "queue_name")
        for k in check_key:
            if not queue_info[k]:
                logger.error("Connect information error! {} can't be empty!".format(k))
                return False

        final_queue_name = "/queue/{}".format(queue_info["queue_name"])
        host_tuple = (queue_info["host"], int(queue_info["port"]))

        # 生成当前机器的consumer_id
        consumer_id = make_consumer_id()

        self.remote_result_queue = ActiveMQQueue(
            host_tuple, queue_info["username"], queue_info["password"],
            final_queue_name, consumer_id
        )

        return True

    def start(self):
        """
        先连接到远程队列，再调用super启动engine
        """
        if not self.__connect_remote_queue():
            logger.error("Can't connect to remote task queue!")
            return False
        super(SenderEngine, self).start()
        return True

    def stop(self):
        """
        先断开队列，再结束engine
        """
        self.remote_result_queue.close()
        super(SenderEngine, self).stop()

    def _worker(self):
        """
        发送结果到远端队列
        """

        logger.info("{} start!".format(self.name))

        app_ctx = self.app_context
        result_buffer_queue: queue.Queue = app_ctx.AppEngines.SPIDER_ENGINE.result_queue

        while self.status == self.EngineStatus.STATUS_RUNNING:
            try:
                result = result_buffer_queue.get_nowait()
            except queue.Empty:
                self.ev.wait(1)
                continue

            self.remote_result_queue.put(result)

        logger.info("{} end!".format(self.name))
