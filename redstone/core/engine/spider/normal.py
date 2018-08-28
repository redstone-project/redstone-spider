#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.core.engine.spider.normal
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    普通的静态爬虫，基于协程池实现

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""

from ..base import MultiCoroutineBaseEngine


class NormalSpiderEngine(MultiCoroutineBaseEngine):

    def __worker(self):
        pass

