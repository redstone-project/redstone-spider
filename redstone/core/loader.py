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
from typing import Dict, Union, TYPE_CHECKING, Optional

from redstone import settings
from redstone.core.engine.base import SingleThreadBaseEngine
from redstone.utils.log import logger

if TYPE_CHECKING:
    from redstone.spiders import SpiderBase


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

    @staticmethod
    def _get_file_md5(filename):
        """
        获取指定文件的MD5值
        :param filename: 待计算MD5值的文件
        :return: 文件的MD5值
        :rtype: str
        """
        with open(filename, "rb") as fp:
            content = fp.read()
            spider_hash = hashlib.md5(content).hexdigest()
        return spider_hash

    def _load_and_update_cache(self, filename):
        """
        根据爬虫的文件名加载spider class，并存入缓存中
        :param filename:
        :return:
            {
                "success": True/False,
                "message": ""
            }
        :rtype: dict
        """

        ret_val = {
            "success": False,
            "message": "Error",
        }

        # 判断爬虫文件是否存在
        spider_file = os.path.join(self.spider_dir, filename)
        if not os.path.exists(spider_file):
            ret_val["message"] = "Spider file not exist!"
            return ret_val

        # 计算文件md5
        spider_hash = self._get_file_md5(spider_file)

        # 检查这个md5是否在cache里
        # 1. 如果不在，添加到cache中
        # 2. 如果在，且hash一致，跳过
        # 3. 如果在，且hash不同，更新hash和class
        pkg_name = filename.split(".")[0]
        pkg_name = pkg_name if isinstance(pkg_name, str) else pkg_name.decode()
        if pkg_name not in self._cache.keys():
            # 不在，添加到cache中
            logger.debug("{} not in cache, load it!".format(pkg_name))
            spider_module = importlib.import_module("redstone.spiders.{}".format(pkg_name))
            logger.debug("clz: {}".format(spider_module))
            # check encoding to fool PyCharm, make it happy!
            self._cache[pkg_name] = (spider_hash, spider_module)

            ret_val["success"] = True
            ret_val["message"] = "Add success!"
            return ret_val
        else:
            # 在，比较hash
            logger.debug("{} in cache, checking hash...".format(pkg_name))
            spider_cache = self._cache[pkg_name]
            if spider_cache[0] == spider_hash:
                # hash 一致，跳过更新
                logger.debug("Same hash, skip...")
                ret_val["success"] = True
                ret_val["message"] = "same hash, no need update."
                return ret_val
            else:
                # <del> 这里可能reload不进来，需要测试下 </del> 测试过了，没问题
                # hash 不一样了，需要更新spider
                logger.debug("spider pkg has be changed, reload...")
                importlib.reload(spider_cache[1])
                self._cache[pkg_name] = (spider_hash, spider_cache[1])

                ret_val["success"] = True
                ret_val["message"] = "spider has been changed, update it."
                return ret_val

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
                # 加载文件并且存到缓存中
                result = self._load_and_update_cache(_filename)
                if not result["success"]:
                    logger.error(result["message"])

            # for test, 如果要调试reload模块，只需要取消下面几行的注释即可
            # inst = self._cache["rss"][1].get_class()
            # inst = inst()
            # inst.run()

        logger.info("{} end!".format(self.name))

    def reload_now(self):
        """
        立即reload爬虫
        """
        logger.info("Receive reload signal!")
        self.ev.set()

    def load_class_by_name(self, spider_name) -> Optional[SpiderBase]:
        logger.debug("Try to load spider: {}".format(spider_name))

        # 把爬虫名字转换成文件名，并提取pkg名
        # ExampleSpider => example_spider => example_spider.py
        pkg_name = [ch if ch.islower() else " " + ch for ch in spider_name]
        pkg_name = "".join(pkg_name).strip()
        pkg_name = pkg_name.replace(" ", "_")
        filename = pkg_name + ".py"

        # 不在缓存中，加载一下
        if pkg_name not in self._cache:
            result = self._load_and_update_cache(filename)
            if not result["success"]:
                logger.error(result["message"])
                return None

        # 直接调用对应爬虫module模块的get_class()方法获取爬虫类
        try:
            return self._cache[pkg_name][1].get_class()
        except AttributeError:
            logger.error("Spider doesn't have 'get_class()' method!")
            return None
