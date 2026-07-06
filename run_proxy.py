#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/9/8 18:49

import asyncio

from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster

from config import BANNER
from proxy.addon import FlowInterceptor

if __name__ == '__main__':
    print(BANNER)
    loop = asyncio.new_event_loop()
    opts = Options(listen_host='0.0.0.0', listen_port=8888)
    m = DumpMaster(opts, loop=loop, with_termlog=False)
    m.options.block_global = False
    m.options.flow_detail = 0
    m.addons.add(FlowInterceptor())
    loop.run_until_complete(m.run())
