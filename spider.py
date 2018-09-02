#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    spider.py
    ~~~~~~~~~

    CLI程序的入口点
    负责启动整个spider项目

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""

import sys
import traceback

from redstone.utils.log import logger
from redstone.core import data as gdata
from redstone.core.application import RedstoneSpiderApplication


def main():
    logger.info("Staring redstone-spider module...")
    gdata.RS_SPIDER_APP = RedstoneSpiderApplication()
    if not gdata.RS_SPIDER_APP.start():
        logger.fatal("Error when starting RS_SPIDER_APP!")

    while True:
        time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        tbe = traceback.TracebackException(exc_type, exc_value, exc_tb)
        full_err = ''.join(tbe.format())
        logger.fatal("Oops! Unhandled exception happened in redstone-spider module. Error: {}".format(e))
        logger.fatal("Full error below: \n{}".format(full_err))
