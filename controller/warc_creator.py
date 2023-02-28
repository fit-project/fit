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
import json
import os
from datetime import datetime
from io import BytesIO
from types import SimpleNamespace

from mitmproxy import http
from warcio import StatusAndHeaders, ArchiveIterator
from warcio.warcwriter import WARCWriter
from wacz.main import create_wacz


class WarcCreator:
    def __init__(self):
        return

    def flow_to_warc(self, flow: http.HTTPFlow, warc_path):

        with open(warc_path, 'ab') as output:

            # create new warcio writer
            writer = WARCWriter(output, gzip=False)
            if len(flow.response.content) > 0:
                content_type = flow.response.headers.get('content-type', '').split(';')[0]
                payload = flow.response.content
                headers = flow.response.headers

                # date from flow is returning as float, needs to be converted
                date_obj = datetime.fromtimestamp(flow.response.timestamp_start)
                # convert the datetime object to an ISO formatted string
                iso_date_str = date_obj.isoformat()

                # create http headers from the information inside the flow
                http_headers = StatusAndHeaders(str(flow.response.status_code) + ' ' + flow.response.reason, headers,
                                                protocol=flow.response.http_version)
                warc_headers = {
                    'WARC-Type': 'resource',
                    'WARC-Target-URI': flow.request.url,
                    'WARC-Source-URI': flow.request.url,
                    'WARC-Date': iso_date_str,
                    'Content-Type': content_type,
                    'Content-Length': str(len(payload))
                }
                # check if payload is in bytes format
                if type(payload) is bytes:
                    payload = BytesIO(payload)

                # create the actual warc record
                record = writer.create_warc_record(flow.request.url, 'response',
                                                   payload=payload,
                                                   http_headers=http_headers,
                                                   warc_headers_dict=warc_headers)
                writer.write_record(record)

    def create_pages(self, pages_path, warc_path):
        # set the header
        header = {
            "format": "json-pages-1.0", "id": "pages", "title": "All Pages",

        }

        with open(os.path.join(pages_path), 'w') as outfile:
            json.dump(header, outfile)

            # read from warc file
            with open(warc_path, 'rb') as stream:
                for record in ArchiveIterator(stream):
                    if record.rec_type == 'response':
                        url = record.rec_headers.get_header('WARC-Target-URI')
                        content_type = record.rec_headers.get_header('Content-Type')
                        if 'text/html' in content_type:
                            id = record.rec_headers.get_header('WARC-Record-ID')
                            ts = record.rec_headers.get_header('WARC-Date')
                            title = record.rec_headers.get_header('WARC-Target-URI')

                            page = {
                                "id": id, "url": url,
                                "ts": ts, "title": title
                            }
                            outfile.write('\n')
                            json.dump(page, outfile)

    def warc_to_wacz(self, pages_path, warc_path, wacz_path):
        class OptionalNamespace(SimpleNamespace):
            def __getattribute__(self, name):
                try:
                    return super().__getattribute__(name)
                except:
                    return None

        res = OptionalNamespace(
            output=wacz_path,
            inputs=[warc_path],
            pages=pages_path,
            detect_pages=False
        )
        return create_wacz(res)
