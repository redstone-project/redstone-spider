#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""

    ~~~~~~~~~~~~~~~~~~


    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017 lightless. All rights reserved
"""

import socket


class IPAddress(object):

    @staticmethod
    def current_ip():
        # 获取本机ip
        hostname = socket.getfqdn(socket.gethostname())
        ip = socket.gethostbyname(hostname)
        return ip
