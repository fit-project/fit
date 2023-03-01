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

from mitmproxy import io, http
from mitmproxy import ctx, flowfilter, http
from scapy.all import *

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
from scapy.layers.inet import IP, TCP


import hashlib
import re
import ssl
import asyncio
from datetime import datetime

import certifi
import mitmproxy.http
from PyQt5.QtCore import QObject, pyqtSignal, QThread

from mitmproxy.tools import main
from mitmproxy.tools.dump import DumpMaster
from controller.warc_creator import WarcCreator as WarcCreatorController
class ProxyServer(QObject):
    proxy_started = pyqtSignal()

    def __init__(self, port, acquisition_directory):
        super().__init__()
        self.port = port
        self.acquisition_directory = acquisition_directory

    async def start(self):
        # set proxy opts
        options = main.options.Options(listen_host='127.0.0.1', listen_port=self.port,
                                       ssl_insecure=True)
        self.master = DumpMaster(options=options)

        addons = [
            FlowReaderAddon(self.acquisition_directory),
            PcapWriter(self.acquisition_directory),
        ]

        self.master.addons.add(*addons)

        try:
            await ctx.master.run()
        except:
            pass


# creating a custom addon to intercept requests and reponses, printing url, status code, headers and content
class FlowReaderAddon:
    def __init__(self, acquisition_directory):
        self.acquisition_directory = acquisition_directory
        self.acq_dir = os.path.join(self.acquisition_directory, 'acquisition_page')
        if not os.path.isdir(self.acq_dir):
            os.makedirs(self.acq_dir)
        return

    def response(self, flow: mitmproxy.http.HTTPFlow):
        # TODO: search a better way to get the resource's name (for same-hocst resources)
        if len(flow.response.content) > 0:
            url = flow.request.url
            # save html first (since it has no extension in the flow)
            if flow.response.headers.get('content-type', '').startswith('text/html'):
                # get html to disk
                html_text = flow.response.content
                with open(f"{self.acq_dir}/{flow.request.pretty_host}.html", "wb") as f:
                    f.write(html_text)

            # get extension for other resources
            content_type = flow.response.headers.get('content-type', '').lower()
            extension = re.search(r'\b(?!text\/)(\w+)\/(\w+)', content_type)
            if extension:
                extension = '.' + extension.group(2)
            else:
                extension = None

            if extension is not None:

                if flow.response.headers.get('content-type', '').split(';')[0].startswith('image/'):
                    # save image to disk
                    with open(
                            f"{self.acq_dir}/{hashlib.md5(url.encode()).hexdigest()}{extension}",
                            "wb") as f:
                        f.write(flow.response.content)
                else:
                    # save other resources to disk
                    with open(
                            f"{self.acq_dir}/{hashlib.md5(url.encode()).hexdigest()}{extension}",
                            "wb") as f:
                        f.write(flow.response.content)

        warc_path = f'{self.acquisition_directory}/acquisition_warc.warc'
        warc_creator = WarcCreatorController()
        warc_creator.flow_to_warc(flow, warc_path)


# creating a custom addon for pcap
class PcapWriter:

    def __init__(self, acquisition_directory):
        self.pkts = []
        self.acquisition_directory = acquisition_directory

    def response(self, flow: http.HTTPFlow):
        pcap_filename = f'{self.acquisition_directory}/mitmproxy_capture.pcap'
        if flow.response:

            pkt = IP(dst=flow.client_conn.peername[0]) / TCP(dport=flow.client_conn.peername[1],
                                                             sport=flow.server_conn.peername[1] / Raw(
                                                                 load=flow.response.content))

            pkt.time = flow.response.timestamp_start
            # self.pkts.append(pkt)
            try:
                print([pkt])
                wrpcap(pcap_filename, [pkt], append=True)
            except Exception as e:
                print('non si può salvare ', e)