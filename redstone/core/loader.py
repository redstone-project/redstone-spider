#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.core.loader
    ~~~~~~~~~~~~~~~~~~~~

    爬虫加载类
        - 根据爬虫的名称获取爬虫的class
        - 定时检测爬虫的文件更改，动态更新

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""
import hashlib

import os
import importlib
from typing import Dict

from redstone import settings
from redstone.core.engine.base import SingleThreadBaseEngine
from redstone.utils.log import logger


class SpiderLoader(SingleThreadBaseEngine):

    def __init__(self):
        super(SpiderLoader, self).__init__()

        """
        self._cache = {
            "spider_pkg_name": ("md5", spider_module)
        }
        """
        self._cache: Dict[str, tuple] = {}

        self.name = "SpiderLoader"

        self.spider_dir = os.path.join(os.path.join(settings.BASE_DIR, "redstone"), "spiders")

    def _worker(self):
        """
        监视spiders文件夹，如果有文件变动，重新计算md5并重新加载
        """

        logger.info("{} start!".format(self.name))

        while self.status == self.EngineStatus.STATUS_RUNNING:

            self.ev.wait(settings.SPIDER_HOT_LOAD_IDLE)
            logger.debug("self._cache: {}".format(self._cache))

            for _filename in os.listdir(self.spider_dir):
                # 跳过双下划线开头的文件和非.py结尾的文件
                if _filename.startswith("__") or not _filename.endswith(".py"):
                    continue
                spider_file = os.path.join(self.spider_dir, _filename)

                # 计算文件的md5
                with open(spider_file, "rb") as fp:
                    content = fp.read()
                    spider_hash = hashlib.md5(content).hexdigest()

                # 检查这个md5是否在cache里
                # 1. 如果不在，添加到cache中
                # 2. 如果在，且hash一致，跳过
                # 3. 如果在，且hash不同，更新hash和class
                pkg_name = _filename.split(".")[0]
                pkg_name = pkg_name if isinstance(pkg_name, str) else pkg_name.decode()
                if pkg_name not in self._cache.keys():
                    # 不在，添加到cache中
                    logger.debug("{} not in cache, load it!".format(pkg_name))
                    spider_module = importlib.import_module("redstone.spiders.{}".format(pkg_name))
                    logger.debug("clz: {}".format(spider_module))
                    # check encoding to fool PyCharm, make it happy!
                    self._cache[pkg_name] = (spider_hash, spider_module)
                else:
                    # 在，比较hash
                    logger.debug("{} in cache, checking hash...".format(pkg_name))
                    spider_cache = self._cache[pkg_name]
                    if spider_cache[0] == spider_hash:
                        logger.debug("Same hash, skip...")
                        continue
                    else:
                        # todo 这里可能reload不进来，需要测试下
                        logger.debug("spider pkg has be changed, reload...")
                        importlib.reload(spider_cache[1])
                        self._cache[pkg_name] = (spider_hash, spider_cache[1])

        logger.info("{} end!".format(self.name))

    def reload_now(self):
        """
        立即reload爬虫
        """
        logger.info("Receive reload signal!")
        self.ev.set()

    def load_class_by_name(self, spider_name):
        # todo finish this
        pass
