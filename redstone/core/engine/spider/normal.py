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
from redstone.utils.log import logger


class NormalSpiderEngine(MultiCoroutineBaseEngine):

    def __init__(self):
        super(NormalSpiderEngine, self).__init__()
        self.name = "NormalSpiderEngine"

    def _worker(self):
        logger.debug("{} start!".format(self.name))
        logger.debug("{} end!".format(self.name))
