#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import asyncio
import logging

from PyQt6.QtCore import QThread
from mitmproxy import ctx
import os.path

import mitmproxy
from mitmproxy import http
from mitmproxy.io import io
from mitmproxy.tools import main
from mitmproxy.tools.dump import DumpMaster

from common.config import LogConfigTools
from controller.mitm import Mitm as MitmController


class MitmProxyWorker(QThread):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.acquisition_directory = None

    def set_dir(self, acquisition_directory):
        self.acquisition_directory = acquisition_directory

    def run(self):
        # create new event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # mitmproxy's creation
        self.proxy_server = MitmProxy(self.port, self.acquisition_directory)
        asyncio.run(self.proxy_server.start())

    def stop_proxy(self):
        try:
            ctx.master.shutdown()
            ctx.master = None
        except:
            pass


class MitmProxy:
    def __init__(self, port, acquisition_directory):
        super().__init__()
        self.port = port
        self.acquisition_directory = acquisition_directory

    async def start(self):
        # Set proxy options
        options = main.options.Options(
            listen_host="127.0.0.1",
            listen_port=self.port,
            ssl_insecure=True,
            tcp_hosts=[".*"],
            udp_hosts=[".*"],
            rawtcp=True,
            rawudp=True,
            mode=["regular"],
        )
        # Create a master object and add addons
        master = DumpMaster(options=options)
        addons = [
            FlowWriterAddon(self.acquisition_directory),
            FlowReaderAddon(self.acquisition_directory),
        ]
        master.addons.add(*addons)
        # disable mitmproxy loggers
        loggers = [logging.getLogger()]
        loggers = loggers + [
            logging.getLogger(name)
            for name in logging.root.manager.loggerDict
            if name not in [__name__, "hashreport"]
        ]
        log_confing = LogConfigTools()
        log_confing.disable_loggers(loggers)

        try:
            await master.run()
        except Exception as e:
            pass


# creating a custom addon to intercept requests and reponses
class FlowReaderAddon:
    def __init__(self, acquisition_directory):
        self.acquisition_directory = acquisition_directory
        self.acq_dir = os.path.join(self.acquisition_directory, "acquisition_page")
        if not os.path.isdir(self.acq_dir):
            os.makedirs(self.acq_dir)
        return

    def response(self, flow: mitmproxy.http.HTTPFlow):
        proxy_controller = MitmController(self.acq_dir)
        proxy_controller.save_resources(flow)


# addon from doc: https://docs.mitmproxy.org/stable/addons-examples/#io-write-flow-file
class FlowWriterAddon:
    def __init__(self, acquisition_directory) -> None:
        self.file = open(f"{acquisition_directory}/flow_dump.txt", "wb")
        self.w = io.FlowWriter(self.file)

    def request(self, flow: http.HTTPFlow) -> None:
        self.w.add(flow)

    def response(self, flow: http.HTTPFlow) -> None:
        self.w.add(flow)
        return
