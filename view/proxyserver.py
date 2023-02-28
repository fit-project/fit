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

import shlex
from time import time
from math import modf
from struct import pack
from subprocess import Popen, PIPE
from mitmproxy import io, http
from scapy.all import *



from common.error import ErrorMessage

import hashlib
import re

import certifi
import mitmproxy.http
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from mitmproxy.tools import main
from mitmproxy.tools.dump import DumpMaster
from controller.warc_creator import WarcCreator as WarcCreatorController

logger_acquisition = logging.getLogger(__name__)
logger_hashreport = logging.getLogger('hashreport')
logger_whois = logging.getLogger('whois')
logger_headers = logging.getLogger('headers')
logger_nslookup = logging.getLogger('nslookup')


class ProxyServer(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.error_msg = ErrorMessage()
        self.run = True
        self.options = None
        self.destroyed.connect(self.stop)

    def set_options(self, port, acquisition_directory):
        self.port = port
        self.acquisition_directory = acquisition_directory

    async def start(self):
        # set proxy opts
        options = main.options.Options(listen_host='127.0.0.1', listen_port=self.port,
                                       ssl_insecure=True)
        self.master = DumpMaster(options=options)

        # addons in mitmproxy are used to provide additional features and customize proxy's behavior
        # this way, we can create custom addons to intercept everything and create the warc/wacz files
        addons = [
            FlowReaderAddon(self.acquisition_directory),
            Addon(lambda: File(f'{self.acquisition_directory}/output.pcap'))
        ]

        self.master.addons.add(*addons)
        try:
            await self.master.run()
        except KeyboardInterrupt:
            self.master.shutdown()
        self.finished.emit()

    def stop(self):
        self.run = False


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
        wacz_path = f'{self.acquisition_directory}/acquisition_wacz.wacz'
        pages_path = f'{self.acquisition_directory}/acquisition_pages.jsonl'
        warc_creator = WarcCreatorController(warc_path, wacz_path, pages_path)
        warc_creator.flow_to_warc(flow)


# creating a custom addon for pcap

class Exporter:

    def __init__(self):
        self.sessions = {}

    def write(self, data):
        raise NotImplementedError()

    def flush(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def header(self):
        data = pack('<IHHiIII', 0xa1b2c3d4, 2, 4, 0, 0, 0x040000, 1)
        self.write(data)

    def packet(self, src_host, src_port, dst_host, dst_port, payload):
        key = '%s:%d-%s:%d' % (src_host, src_port, dst_host, dst_port)
        session = self.sessions.get(key)
        if session is None:
            session = {'seq': 1}
            self.sessions[key] = session
        seq = session['seq']
        total = len(payload) + 20 + 20

        tcp_args = [src_port, dst_port, seq, 0, 0x50, 0x18, 0x0200, 0, 0]
        tcp = pack('>HHIIBBHHH', *tcp_args)
        ipv4_args = [0x45, 0, total, 0, 0, 0x40, 6, 0]
        ipv4_args.extend(map(int, src_host.split('.')))
        ipv4_args.extend(map(int, dst_host.split('.')))
        ipv4 = pack('>BBHHHBBHBBBBBBBB', *ipv4_args)
        link = b'\x00' * 12 + b'\x08\x00'

        usec, sec = modf(time())
        usec = int(usec * 1000 * 1000)
        sec = int(sec)
        size = len(link) + len(ipv4) + len(tcp) + len(payload)
        head = pack('<IIII', sec, usec, size, size)

        self.write(head)
        self.write(link)
        self.write(ipv4)
        self.write(tcp)
        self.write(payload)
        session['seq'] = seq + len(payload)

    def packets(self, src_host, src_port, dst_host, dst_port, payload):
        limit = 40960
        for i in range(0, len(payload), limit):
            self.packet(src_host, src_port,
                        dst_host, dst_port,
                        payload[i:i + limit])


class File(Exporter):

    def __init__(self, path):
        super().__init__()
        self.path = path
        if os.path.exists(path):
            self.file = open(path, 'ab')
        else:
            self.file = open(path, 'wb')
            self.header()

    def write(self, data):
        self.file.write(data)

    def flush(self):
        self.file.flush()

    def close(self):
        self.file.close()


class Pipe(Exporter):

    def __init__(self, cmd):
        super().__init__()
        self.proc = Popen(shlex.split(cmd), stdin=PIPE)
        self.header()

    def write(self, data):
        self.proc.stdin.write(data)

    def flush(self):
        self.proc.stdin.flush()

    def close(self):
        self.proc.terminate()
        self.proc.poll()


class Addon:

    def __init__(self, createf):
        self.createf = createf
        self.exporter = None

    def load(self, entry):  # pylint: disable = unused-argument
        self.exporter = self.createf()

    def done(self):
        self.exporter.close()
        self.exporter = None

    def response(self, flow):
        client_addr = list(flow.client_conn.ip_address[:2])
        server_addr = list(flow.server_conn.ip_address[:2])
        client_addr[0] = client_addr[0].replace('::ffff:', '')
        server_addr[0] = server_addr[0].replace('::ffff:', '')
        self.export_request(client_addr, server_addr, flow.request)
        self.export_response(client_addr, server_addr, flow.response)
        self.exporter.flush()

    def export_request(self, client_addr, server_addr, r):
        proto = '%s %s %s\r\n' % (r.method, r.path, r.http_version)
        payload = bytearray()
        payload.extend(proto.encode('ascii'))
        payload.extend(bytes(r.headers))
        payload.extend(b'\r\n')
        payload.extend(r.raw_content)
        self.exporter.packets(*client_addr, *server_addr, payload)

    def export_response(self, client_addr, server_addr, r):
        headers = r.headers.copy()
        if r.http_version.startswith('HTTP/2'):
            headers.setdefault('content-length', str(len(r.raw_content)))
            proto = '%s %s\r\n' % (r.http_version, r.status_code)
        else:
            headers.setdefault('Content-Length', str(len(r.raw_content)))
            proto = '%s %s %s\r\n' % (r.http_version, r.status_code, r.reason)

        payload = bytearray()
        payload.extend(proto.encode('ascii'))
        payload.extend(bytes(headers))
        payload.extend(b'\r\n')
        payload.extend(r.raw_content)
        self.exporter.packets(*server_addr, *client_addr, payload)
