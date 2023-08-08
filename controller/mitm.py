#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import hashlib
import threading
from mitmproxy import http

import os.path
import mitmproxy.http


class Mitm:
    def __init__(self, acq_dir):
        self.acq_dir = acq_dir

    def save_html(self, flow: mitmproxy.http.HTTPFlow):
        if flow.response.headers.get("content-type", "").startswith("text/html"):
            # write html to disk
            html_text = flow.response.content
            if len(html_text) > 0:
                filename = self.__calculate_md5(flow.request.url)
                filepath = os.path.join(self.acq_dir, filename)

                if not os.path.exists(f"{filepath}.html"):
                    with open(f"{filepath}.html", "wb") as f:
                        f.write(html_text)
        return

    def save_resources(self, flow: mitmproxy.http.HTTPFlow):
        # save resources in separate threads
        self.save_html(flow)

        resources_thread = threading.Thread(target=self.save_content, args=(flow,))
        resources_thread.start()
        return

    def save_content(self, flow: mitmproxy.http.HTTPFlow):
        # save every other resource in the acquisition dir
        content_types = [
            "image/jpeg",
            "image/png",
            "application/json",
            "application/javascript",
            "audio/mpeg",
            "text/css",
            "text/javascript",
            "image/gif",
        ]
        if flow.response.headers.get("content-type", "").split(";")[0] in content_types:
            filename = os.path.basename(flow.request.url)

            char_remov = ["?", "<", ">", "*", "|", '"', "\\", "/", ":"]
            for char in char_remov:
                filename = filename.replace(char, "-")

            filepath = f"{self.acq_dir}/{filename}"
            try:
                with open(filepath, "wb") as f:
                    f.write(flow.response.content)
            except:
                pass  # could not write

    def __calculate_md5(self, name):
        md5 = hashlib.md5()
        bytes = name.encode("utf-8")
        md5.update(bytes)
        md5_id = md5.hexdigest()
        return md5_id
