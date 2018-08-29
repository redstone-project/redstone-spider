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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from redstone.core.application import RedstoneSpiderApplication


class CommonBaseEngine(object, metaclass=abc.ABCMeta):
    """
    所有类型engine的通用基类，定义了各种接口
    """
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
