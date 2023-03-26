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
import mimetypes
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from mitmproxy import http

import hashlib
import re
import os.path

import mitmproxy.types
from mitmproxy import http
from mitmproxy import io
import mitmproxy.http
from PyQt5.QtCore import QObject, pyqtSignal
from mitmproxy.tools import main
from mitmproxy.tools.dump import DumpMaster

from controller.warc_creator import WarcCreator as WarcCreatorController


class ProxyServer:
    def __init__(self, acq_dir):
        self.acq_dir = acq_dir

    def save_html(self, flow: mitmproxy.http.HTTPFlow):

        if flow.response.headers.get('content-type', '').startswith('text/html'):
            # write html to disk
            html_text = flow.response.content
            if len(html_text) > 0:
                url = flow.request.pretty_url
                parsed_url = urlparse(url)
                domain = parsed_url.netloc
                path = parsed_url.path
                path = path.replace('//', '-')
                filename = f"{domain}{path.replace('/', '-')}.html"
                filepath = os.path.join(self.acq_dir, filename)

                if not os.path.exists(f"{filepath}"):
                    with open(f"{filepath}", "wb") as f:
                        f.write(html_text)
        return

    def save_resources(self, flow: mitmproxy.http.HTTPFlow):
        # save every other resource in the acquisition dir
        content_types = ["image/jpeg", "image/png", "application/json", "application/javascript",
                         "video/mp4", "audio/mpeg", "text/css", "text/javascript", "image/gif"]
        if flow.response.headers.get('content-type', '').split(';')[0] in content_types:
            filename = flow.request.url.split("/")[-1]
            content_type, encoding = mimetypes.guess_type(filename)
            if not content_type:
                content_type = flow.response.headers.get('content-type', '').split(';')[0]
            if content_type:
                extension = mimetypes.guess_extension(content_type)
                if extension:
                    filename += extension
                    filepath = f"{self.acq_dir}/{filename}"
                    with open(filepath, "wb") as f:
                        f.write(flow.response.content)
        return

    def save_embedded_videos(self, flow: mitmproxy.http.HTTPFlow):

        return