#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.settings.example
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    示例配置文件
    使用时，请根据部署环境，复制该文件到dev.py 或 pre.py 或 prod.py

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""

import os


# 基础信息
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("BASE_DIR: " + BASE_DIR)

# LOG相关设置
LOG_TO_FILE = True
LOG_FILENAME = "redstone-spider.log"
LOG_PATH = os.path.join(BASE_DIR, "logs")

# 爬虫加载设置
SPIDER_HOT_LOAD_IDLE = 30

# 爬虫工作线程数量
SPIDER_POOL_SIZE = 32

# 服务端队列信息设置
ACTIVEMQ_HOST = "127.0.0.1"
ACTIVEMQ_PORT = "61613"
ACTIVEMQ_USERNAME = "redstone"
ACTIVEMQ_PASSWORD = "123456"

# 任务队列名称
ACTIVEMQ_QUEUES = {
    "coroutine_task": "redstone.coroutine.task",
    "thread_task": "redstone.thread.task",
    # 返回爬虫结果的队列名称
    "spider_result": "redstone.result.spider_result",
}
