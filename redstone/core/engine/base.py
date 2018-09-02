#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.core.engine.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    BaseEngine部分

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""
from __future__ import annotations

import abc
import threading
import multiprocessing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redstone.core.application import RedstoneSpiderApplication


class CommonBaseEngine(object, metaclass=abc.ABCMeta):
    """
    所有类型engine的通用基类，定义了各种接口
    """

    class EngineStatus:
        STATUS_READY = 0x00
        STATUS_RUNNING = 0x01
        STATUS_STOP = 0x02

    def __init__(self):
        super(CommonBaseEngine, self).__init__()

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def is_alive(self):
        pass

    @abc.abstractmethod
    def _worker(self):
        # 要用单下划线声明成protected方法，如果用双下划线代表private
        # 则子类无法override
        pass


class MultiCoroutineBaseEngine(CommonBaseEngine):
    """
    协程池engine的基类
    """

    def __init__(self):
        super(MultiCoroutineBaseEngine, self).__init__()
        self.name = "default-multi-coroutine-engine"
        self.main_thread: threading.Thread = None
        self.app_context: RedstoneSpiderApplication = None

    def start(self):
        pass

    def stop(self):
        pass

    def is_alive(self):
        pass

    @abc.abstractmethod
    def _worker(self):
        pass


class MultiThreadBaseEngine(CommonBaseEngine):
    """
    线程池engine的基类
    """

    def __init__(self, pool_size=None):
        super(MultiThreadBaseEngine, self).__init__()
        self.name = "default-multi-thread-engine"

        self.thread_pool = []
        self.pool_size = pool_size if pool_size else multiprocessing.cpu_count() * 2 + 1

        self.app_context: RedstoneSpiderApplication = None

        self.ev = threading.Event()
        self.status = self.EngineStatus.STATUS_READY

    def start(self):
        self.status = self.EngineStatus.STATUS_RUNNING
        self.thread_pool = [
            threading.Thread(target=self._worker, name="{}-{}".format(self.name, idx)) for idx in
            range(self.pool_size)
        ]
        _ = [thread.start() for thread in self.thread_pool]
        return True

    def stop(self):
        self.status = self.EngineStatus.STATUS_STOP
        self.ev.set()

    def is_alive(self):
        return True if any([thread.is_alive() for thread in self.thread_pool]) else False

    @abc.abstractmethod
    def _worker(self):
        pass
