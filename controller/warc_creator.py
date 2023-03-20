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
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from mitmproxy import http
from warcio import StatusAndHeaders, ArchiveIterator
from warcio.warcwriter import WARCWriter
from wacz.main import create_wacz


# thanks to Andrea Lazzarotto @lazza for the contribution on the warc and wacz creation
class OptionalNamespace(SimpleNamespace):
    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except:
            return None


class PosixZipInfo(zipfile.ZipInfo):
    def __init__(self, filename="NoName", date_time=(1980, 1, 1, 0, 0, 0)):
        filename = Path(filename).as_posix()
        super().__init__(filename=filename, date_time=date_time)


class WarcCreator:
    def __init__(self):
        return

    def warcinfo(self, output_prefix):
        warc_path = str(output_prefix.with_suffix(".warc"))
        with open(warc_path, 'wb') as output:
            # create new warcio writer
            writer = WARCWriter(output, gzip=False)
            warcinfo_content = {
                'software': 'Freezing Internet Tool - FIT',
                'format': 'WARC File Format 1.0'
            }
            record = writer.create_warcinfo_record(warc_path, info=warcinfo_content)
            writer.write_record(record)

    def request_to_warc(self, flow: http.HTTPFlow, output_prefix):
        warc_path = output_prefix.with_suffix(".warc")
        with open(warc_path, 'ab') as output:
            # create new warcio writer
            writer = WARCWriter(output, gzip=False)
            content_type = flow.request.headers.get('content-type', '')

            payload = flow.request.content
            headers = flow.request.headers

            # date from flow is returning as float, needs to be converted
            date_obj = datetime.fromtimestamp(flow.request.timestamp_start)
            # convert the datetime object to an ISO formatted string
            iso_date_str = date_obj.isoformat()
            # create http headers from the information inside the flow

            http_headers = StatusAndHeaders(
                statusline=f"{flow.request.method} {flow.request.path}", headers=headers,
                protocol=flow.request.http_version)

            warc_headers = {
                'WARC-Type': 'request',
                'WARC-Target-URI': flow.request.url,
                'WARC-Date': iso_date_str,
                'Content-Type': content_type,
                'Content-Length': str(len(payload)),
                'WARC-Concurrent-To': self.get_response_record_id(flow,output_prefix)
            }

            if type(payload) is bytes:
                payload = BytesIO(payload)

            # create the actual warc record
            record = writer.create_warc_record(flow.request.url, 'request',
                                               payload=payload,
                                               http_headers=http_headers,
                                               warc_headers_dict=warc_headers)

            writer.write_record(record)

    def response_to_warc(self, flow: http.HTTPFlow, output_prefix):

        warc_path = output_prefix.with_suffix(".warc")

        with open(warc_path, 'ab') as output:
            # create new warcio writer
            writer = WARCWriter(output, gzip=False)
            content_type = flow.response.headers.get('content-type', '')
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
                'WARC-Target-URI': flow.request.url,
                'WARC-Date': iso_date_str,
                'Content-Type': content_type,
                'Content-Length': str(len(payload))
            }

            if type(payload) is bytes:
                payload = BytesIO(payload)

            # create the actual warc record
            record = writer.create_warc_record(flow.request.url, 'response',
                                               payload=payload,
                                               http_headers=http_headers,
                                               warc_headers_dict=warc_headers)
            writer.write_record(record)

    def create_pages(self, path):
        warc_path = path.with_suffix(".warc")
        pages_path = path.with_suffix(".json")
        # set the header
        header = {
            "format": "json-pages-1.0", "id": "pages", "title": "All Pages",

        }
        if os.path.exists(warc_path):
            with open(os.path.join(pages_path), 'w') as outfile:
                json.dump(header, outfile)

                # read from warc file
                with open(warc_path, 'rb') as stream:
                    for record in ArchiveIterator(stream):
                        if record.rec_type == 'request':
                            url = record.rec_headers.get_header('WARC-Target-URI')
                            content_type = record.rec_headers.get_header('Content-Type')
                            if 'text/html' in content_type:
                                html = record.content_stream().read()
                                if len(html) > 0:
                                    id = record.rec_headers.get_header('WARC-Record-ID')
                                    ts = record.rec_headers.get_header('WARC-Date')
                                    title = record.rec_headers.get_header('WARC-Target-URI')

                                    page = {
                                        "id": id, "url": url,
                                        "ts": ts, "title": title
                                    }
                                    outfile.write('\n')
                                    json.dump(page, outfile)

    def warc_to_wacz(self, path):
        warc_path = path.with_suffix(".warc")
        wacz_output = path.with_suffix(".wacz")
        pages_path = path.with_suffix(".json")
        warc_file_path = Path(warc_path).as_posix()
        pages_path = Path(pages_path).as_posix()
        wacz_output_path = Path(wacz_output).as_posix()

        zipfile.ZipInfo = PosixZipInfo

        res = OptionalNamespace(
            output=wacz_output_path,
            inputs=[warc_file_path],
            pages=pages_path,
            detect_pages=False
        )
        create_wacz(res)
        os.remove(pages_path)
        os.remove(warc_path)

    def get_response_record_id(self, flow: http.HTTPFlow,output_prefix):
        # find the most recent request with the same WARC-Target-URI as the response
        # we need to connect request to the response in order to correctly load the resources
        warc_path = str(output_prefix.with_suffix(".warc"))
        with open(warc_path, 'rb') as output:

            for record in ArchiveIterator(output):
                if record.rec_type == 'response' and record.rec_headers.get('WARC-Target-URI') == flow.request.url:
                    most_recent_response = record
            return most_recent_response.rec_headers.get('WARC-Record-ID')
