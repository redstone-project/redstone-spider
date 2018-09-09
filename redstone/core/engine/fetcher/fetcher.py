#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.core.engine.fetcher.fetcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    fetcher 模块，从远端的ActiveMQ接收任务消息

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""
import threading
import time
from typing import Dict

from redstone.utils.ip import IPAddress
from redstone.utils.log import logger
from ..base import SingleThreadBaseEngine
from redstone.utils.activemq import ActiveMQQueue
from .listener import FetcherListener


class FetcherEngine(SingleThreadBaseEngine):

    def __init__(self, queue_info: Dict[str, str]):
        super(FetcherEngine, self).__init__()

        # engine 名称
        self.name = "FetchEngine"

        # 工作线程
        self.thread: threading.Thread = None

        # Running Status, Event Flag
        self.status = self.EngineStatus.STATUS_RUNNING
        self.ev = threading.Event()

        # 远程的任务队列
        self.remote_task_queue: ActiveMQQueue = None

        # 远程队列的相关
        # queue_info = {
        #   "host":
        #   "port":
        #   "username":
        #   "password":
        #   "queue_name":
        # }
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

        # 生成当前机器的consumer id
        # 当前机器的IP + "|" + "当前的timestamp（精确到秒）"
        consumer_id = "{ip}|{timestamp}".format(ip=IPAddress.current_ip(), timestamp=int(time.time()))

        self.remote_task_queue = ActiveMQQueue(
            host_tuple, queue_info["username"], queue_info["password"],
            final_queue_name, consumer_id
        )

        return True

    def start(self):
        """
        先连接远程队列，再调用super启动engine
        """

        if not self.__connect_remote_queue():
            logger.error("Can't connect to remote task queue!")
            return False
        super(FetcherEngine, self).start()
        return True

    def stop(self):
        """
        先断开队列，再结束engine
        """
        self.remote_task_queue.close()
        super(FetcherEngine, self).stop()

    def _worker(self):
        """
        连接远程队列，保活
        """

        logger.info("{} start!".format(self.name))

        # 把线程订阅到对应的queue上
        # 添加这个确保prefetch数量 headers={'activemq.prefetchSize': 1}
        self.remote_task_queue.set_listener("", FetcherListener(self))
        self.remote_task_queue.connect()
        self.remote_task_queue.subscribe()

        # 保活Fetcher线程
        while self.status == self.EngineStatus.STATUS_RUNNING:
            self.ev.wait(1)

        logger.info("{} end!".format(self.name))
