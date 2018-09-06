#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.core.engine.fetcher.thread
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    fetcher engine
    负责从队列中接收线程任务，并执行对应的任务

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""
import json
import threading
from typing import List, TYPE_CHECKING, Optional

import stomp

from redstone import settings
from redstone.core.engine.base import MultiThreadBaseEngine
from redstone.spiders import SpiderBase
from redstone.utils.activemq import ActiveMQQueue
from redstone.utils.ip import IPAddress
from redstone.utils.log import logger

if TYPE_CHECKING:
    from redstone.core.application import RedstoneSpiderApplication


class AgentListener(stomp.ConnectionListener):
    """
    Agent Listener
    异步接收消息，并且执行
    """

    def __init__(self, current_name, thread_context, current_idx, consumer_id):
        super(AgentListener, self).__init__()
        self.current_name = current_name

        # 运行当前callback的线程上下文
        self.thread_context: ThreadFetchAgent = thread_context

        # 当前线程的ID，用于到上下文中获取数据使用
        self.current_idx = current_idx

        # 消费者ID，对于同一个队列来讲，这个应该是唯一的
        self.consumer_id = consumer_id

        # 获取spider loader
        self.spider_loader = self.thread_context.app_context.AppEngines.SPIDER_LOADER

    def on_message(self, headers, body):
        """
        接收消息
        :param headers:
        :param body:
        :return:
        """

        try:
            message_id = headers["message-id"]
            logger.debug("Receive message, id: {}, body: {}".format(message_id, body))

            # 解析消息内容
            message = json.loads(body)
            feed_url = message["feed_url"]
            feed_name = message["feed_name"]
            feed_id = message["feed_id"]
            spider_name = message["spider_name"]  # use this to load spider class

            # 加载爬虫类 并实例化
            spider_cls: Optional[SpiderBase] = self.spider_loader.load_class_by_name(spider_name)
            if spider_cls is None:
                return False
            # PyCharm并不能检测到我在实例化一个对象，它认为我在调用一个函数
            spider_instance: SpiderBase = spider_cls()

            # 设置爬虫运行所需要的数据
            # spider_instance.set_params()

            # 运行爬虫
            spider_instance.run()

            # 获取爬虫结果
            result = spider_instance.get_result()

            # result_queue.put(result)

            return True
        finally:
            # 保证无论是否执行成功，都ACK消息
            self.thread_context.task_queues[self.current_idx].make_ack(headers["message-id"], self.consumer_id)

    def on_error(self, headers, body):
        logger.error("Error on receive message from queue!")


class ThreadFetchAgent(MultiThreadBaseEngine):

    def __init__(self, app_context):
        super(ThreadFetchAgent, self).__init__()
        self.name = "ThreadFetcher"

        self.app_context: RedstoneSpiderApplication = app_context

        self.task_queues: List[ActiveMQQueue] = None

    @staticmethod
    def __get_queue(queue_name, consumer_id):
        """
        获取队列信息，并创建ActiveMQ队列对象
        :return:
            dict["success"]
            dict["message"]
            dict["task_queue"]
        :rtype: dict
        """
        final_queue_name = "/queue/{}".format(queue_name)
        host_info = (settings.ACTIVEMQ_HOST, int(settings.ACTIVEMQ_PORT))
        _queue = ActiveMQQueue(
            host_info,
            settings.ACTIVEMQ_USERNAME,
            settings.ACTIVEMQ_PASSWORD,
            final_queue_name,
            consumer_id
        )

        return {
            "success": True,
            "message": "connect success!",
            "task_queue": _queue,
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

        # 生成当前的consumer id
        # 规则："".join([当期机器的IP, "_", current_idx])
        consumer_id = "{ip}__{idx}".format(ip=IPAddress.current_ip().replace(".", "_"), idx=current_idx)

        # 获取Task ActiveMQ队列对象
        task_queue_name = settings.ACTIVEMQ_QUEUES["thread_task"]
        result_queue_name = settings.ACTIVEMQ_QUEUES["result_spider"]
        result = self.__get_queue(task_queue_name, consumer_id)
        if not result["success"]:
            raise RuntimeError("Connect to thread task queue failed!")

        # 设置listener并且连接到ActiveMQ队列
        task_queue = result["task_queue"]
        self.task_queues[current_idx] = task_queue
        self.task_queues[current_idx].set_listener(
            "", AgentListener(current_name, self, current_idx, consumer_id)
        )
        self.task_queues[current_idx].connect()

        # 订阅到指定队列
        self.task_queues[current_idx].subscribe(current_idx)

        # 等待结束信号
        while self.status == self.EngineStatus.STATUS_RUNNING:
            # 如果是running的话，就保活当前线程，除非接到停止信号
            self.ev.wait(1)

        logger.debug("{} end!".format(current_name))
