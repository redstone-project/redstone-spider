#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    redstone.utils.common
    ~~~~~~~~~~~~~~~~~~~~~


    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""

import time

from .ip import IPAddress


def make_consumer_id():
    return "{}|{}".format(IPAddress.current_ip(), str(time.time()))
