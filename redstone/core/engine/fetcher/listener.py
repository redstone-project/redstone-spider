#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.core.engine.fetcher.listener
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    FetcherEngine中，远程队列的listener，接收到的消息都在这里处理

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""

import typing

import stomp

from redstone.utils.log import logger

if typing.TYPE_CHECKING:
    from .fetcher import FetcherEngine


class FetcherListener(stomp.ConnectionListener):
    """
    Listener，异步接收消息
    """

    def __init__(self, thread_ctx):
        self.fetcher_thread_ctx: FetcherEngine = thread_ctx

    def on_message(self, headers, body):
        """
        不停的从队列中获取消息，并且放到本地的buffer queue中
        只有当确实放到了buffer queue中之后，再回复ACK接收新消息
        """

        # 检查线程的状态，如果线程已经结束，不再处理任何消息
        if self.fetcher_thread_ctx.status != self.fetcher_thread_ctx.EngineStatus.STATUS_RUNNING:
            return

        # 获取buffer queue
        redstone_app = self.fetcher_thread_ctx.app_context
        buffer_queue = redstone_app.AppEngines.WORKER_ENGINE.buffer_queue

        try:
            message_id = headers["message_id"]
            logger.info("Receive message, id: {}, body: {}".format(message_id, body))

            # 直接把消息放到本地的buffer queue中
            # todo：考虑把消息封装到一个dataclass里，写的时候比较方便
            buffer_queue.put(body)

        finally:
            # 保证一定会发送ACK确认消息
            message_id = headers["message_id"]
            self.fetcher_thread_ctx.remote_task_queue.make_ack(message_id)
