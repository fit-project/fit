#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
#
# Copyright (c) 2022 FIT-Project and others
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
######
import logging
from pathlib import Path
from mitmproxy import http
import os.path

import mitmproxy.types
from mitmproxy import http
from mitmproxy import io
import mitmproxy.http
from PyQt5.QtCore import QObject, pyqtSignal
from mitmproxy.tools import main
from mitmproxy.tools.dump import DumpMaster


from controller.proxyserver import ProxyServer as ProxyServerController


class ProxyServer(QObject):
    proxy_started = pyqtSignal()

    def __init__(self, port, acquisition_directory):
        super().__init__()
        self.port = port
        self.acquisition_directory = acquisition_directory



    async def start(self):

        # Set proxy options
        options = main.options.Options(
            listen_host='127.0.0.1',
            listen_port=self.port,
            ssl_insecure=True,
            tcp_hosts=[".*"],
            udp_hosts=[".*"],
            rawtcp=True,
            rawudp=True,
            mode=['regular']
        )
        # Create a master object and add addons
        master = DumpMaster(options=options)
        addons = [
            FlowReaderAddon(self.acquisition_directory),
            FlowWriterAddon(self.acquisition_directory)
        ]
        master.addons.add(*addons)

        try:
            await master.run()
        except Exception as e:
            pass


# addon from doc: https://docs.mitmproxy.org/stable/addons-examples/#io-write-flow-file
class FlowWriterAddon:
    def __init__(self, acquisition_directory) -> None:
        self.w = mitmproxy.io.FlowWriter(open(f'{acquisition_directory}/flow_dump.txt', "wb"))  # standard: .mitm

    def request(self, flow: http.HTTPFlow) -> None:
        self.w.add(flow)

    def response(self, flow: http.HTTPFlow) -> None:
        self.w.add(flow)


# creating a custom addon to intercept requests and reponses
class FlowReaderAddon:
    def __init__(self, acquisition_directory):
        self.acquisition_directory = acquisition_directory
        self.acq_dir = os.path.join(self.acquisition_directory, 'acquisition_page')
        if not os.path.isdir(self.acq_dir):
            os.makedirs(self.acq_dir)
        return

    def response(self, flow: mitmproxy.http.HTTPFlow):
        proxy_controller = ProxyServerController(self.acq_dir)
        proxy_controller.save_resources(flow)

