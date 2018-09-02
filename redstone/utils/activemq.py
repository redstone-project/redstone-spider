#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.utils.activemq
    ~~~~~~~~~~~~~~~~~~~~~~~

    封装过一层的ActiveMQ队列

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""

from typing import Tuple

import stomp


class ActiveMQQueue(object):
    """
    封装过的一层ActiveMQ，集成了常用操作
    """

    def __init__(self, target: Tuple[str, int], username, password, queue_name):
        super(ActiveMQQueue, self).__init__()
        self._target = target
        self._username = username
        self._password = password

        self.queue_name = queue_name
        self.queue: stomp.StompConnection11 = None

    def connect(self):
        self.queue = stomp.Connection([self._target])
        self.queue.connect(self._username, self._password, wait=True)

    def set_listener(self, name, listener):
        self.queue.set_listener(name, listener)

    def subscribe(self, idx):
        self.queue.subscribe(self.queue_name, idx, "client")

    def close(self):
        if self.queue:
            self.queue.disconnect()

    def __repr__(self) -> str:
        return "({}, name: {})".format(self._target, self.queue_name)

    def __str__(self) -> str:
        return "({}, name: {})".format(self._target, self.queue_name)
