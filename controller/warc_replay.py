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
import http.server
import os

from PyQt5.QtCore import pyqtSignal, QThread

from common import utility


def parse_range_header(self, f):
    # Extract start and end byte positions from Range header
    byte_range = self.headers.get('Range')
    if not byte_range:
        return 0, f.size - 1
    start, end = byte_range.split('=')[1].split('-')

    # Calculate start and end byte positions
    start = int(start)
    end = int(end) if end else f.size - 1
    return start, end


class Handler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()

    def do_GET(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            self.send_error(404, "File not found")
            return None
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header('Content-type', self.guess_type(path))
        self.send_header('Content-Length', str(os.fstat(f.fileno()).st_size))
        self.send_header('Last-Modified', self.date_time_string(int(os.path.getmtime(path))))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        self.copyfile(f, self.wfile)
        f.close()


class WarcReplay(QThread):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.stop_server = False
        self.httpd = None
        self.port = utility.find_free_port()

    def get_port(self):
        return self.port

    def run(self):
        server_class = http.server.HTTPServer
        handler_class = Handler
        server_address = ('', self.port)
        self.httpd = server_class(server_address, handler_class)
        while not self.stop_server:
            self.httpd.handle_request()
        self.httpd.server_close()
        self.finished.emit()
