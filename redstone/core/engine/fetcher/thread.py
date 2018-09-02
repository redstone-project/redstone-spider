#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.core.engine.fetcher.fetcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    fetcher engine
    负责从队列中接收线程任务，并执行对应的任务

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""
import json
import threading
from typing import List

import stomp

from redstone import settings
from redstone.core.engine.base import MultiThreadBaseEngine
from redstone.utils.activemq import ActiveMQQueue
from redstone.utils.log import logger


class AgentListener(stomp.ConnectionListener):
    """
    Agent Listener
    异步接收消息，并且执行
    """

    def __init__(self, current_name, thread_context):
        super(AgentListener, self).__init__()
        self.current_name = current_name
        self.thread_context: ThreadFetchAgent = thread_context

    def on_message(self, headers, body):
        """
        接收消息
        :param headers:
        :param body:
        :return:
        """

        message_id = headers["message-id"]
        logger.debug("Receive message, id: {}, body: {}".format(message_id, body))

        # 解析消息内容
        message = json.loads(body)
        url = message["feed_url"]

    def on_error(self, headers, body):
        pass


class ThreadFetchAgent(MultiThreadBaseEngine):

    def __init__(self):
        super(ThreadFetchAgent, self).__init__()
        self.name = "ThreadFetcher"

        self.task_queues: List[ActiveMQQueue] = None

    @staticmethod
    def __get_queue():
        """
        获取队列信息，并创建ActiveMQ队列对象
        :return:
            dict["success"]
            dict["message"]
            dict["task_queue"]
        :rtype: dict
        """
        queue_name = settings.ACTIVEMQ_QUEUES.get("thread_task")
        if not queue_name:
            return {
                "success": False,
                "message": "Can't get queue name for 'thread_task' queue!",
                "task_queue": None,
            }

        queue_name = "/queue/{}".format(queue_name)
        task_queue = ActiveMQQueue(
            (settings.ACTIVEMQ_HOST, int(settings.ACTIVEMQ_PORT)),
            settings.ACTIVEMQ_USERNAME, settings.ACTIVEMQ_PASSWORD,
            queue_name
        )

        return {
            "success": True,
            "message": "connect success!",
            "task_queue": task_queue,
        }

    def stop(self):
        super(ThreadFetchAgent, self).stop()
        _ = [x.close() for x in self.task_queues]

    def _worker(self):
        """
        工作线程
        """
        current_name = threading.current_thread().getName()
        logger.debug("{} start!".format(current_name))

        # 获取当前线程的序号
        current_idx = int(current_name.split("-")[0])

        # 获取ActiveMQ队列对象
        result = self.__get_queue()
        if not result["success"]:
            raise RuntimeError("Connect to thread task queue failed!")

        # 设置listener并且连接到ActiveMQ队列
        task_queue = result["task_queue"]
        self.task_queues[current_idx] = task_queue
        self.task_queues[current_idx].set_listener("", AgentListener(current_name, self))
        self.task_queues[current_idx].connect()

        # 订阅到指定队列
        self.task_queues[current_idx].subscribe(current_idx)

        # 等待结束信号
        while self.status == self.EngineStatus.STATUS_RUNNING:
            # 如果是running的话，就保活当前线程，除非接到停止信号
            self.ev.wait(1)

        logger.debug("{} end!".format(current_name))
