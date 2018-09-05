#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""

    ~~~~~~~~~~~~~~~~~~


    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""

from . import SpiderBase
from redstone.utils.log import logger


class RSSSpider(SpiderBase):

    def run(self):
        logger.info("RSS Spider running!23333")


def get_class():
    return RSSSpider
