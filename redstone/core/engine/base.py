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

import abc


class MultiCoroutineBaseEngine(object, metaclass=abc.ABCMeta):

    def __init__(self):
        super(MultiCoroutineBaseEngine, self).__init__()

    def start(self):
        pass

    def stop(self):
        pass

    def is_alive(self):
        pass

    @abc.abstractmethod
    def __worker(self):
        pass
