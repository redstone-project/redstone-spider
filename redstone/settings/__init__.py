#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.settings
    ~~~~~~~~~~~~~~~~~

    配置模块

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""

import os

current_env = os.getenv("REDSTONE_SPIDER_ENV", None)
print("REDSTONE_SPIDER_ENV: {}".format(current_env))

if not current_env or current_env.lower() == "dev":
    from .dev import *
elif current_env.lower() == "pre":
    from .pre import *
elif current_env.lower() == "prod":
    from .prod import *
else:
    from .dev import *
