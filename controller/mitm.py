#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import hashlib
import string
import threading
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from mitmproxy import http

import os.path
import mitmproxy.http


class Mitm:
    def __init__(self, acq_dir):
        self.acq_dir = acq_dir
        self.soup = None

    def save_html(self, flow: mitmproxy.http.HTTPFlow):
        if flow.response.headers.get("content-type", "").startswith("text/html"):
            # write html to disk
            html_text = flow.response.content
            if len(html_text) > 0:
                soup = BeautifulSoup(html_text, "html.parser")
                title = soup.title.string.strip()

                self.filename_page = f"{self.__clean_title(title)}"
                filepath = os.path.join(self.acq_dir, self.filename_page)

                if not os.path.exists(f"{filepath}.html"):
                    with open(f"{filepath}.html", "wb") as f:
                        f.write(html_text)

    def save_resources(self, flow: mitmproxy.http.HTTPFlow):
        # save resources in separate threads
        self.filename_page = self.get_file_name(flow)
        self.soup = BeautifulSoup(flow.response.content, "html.parser")
        resources_thread = threading.Thread(target=self.save_content, args=(flow,))
        resources_thread.start()
        resources_thread.join()
        self.save_html(flow)

    def get_file_name(self, flow: mitmproxy.http.HTTPFlow):
        if flow.response.headers.get("content-type", "").startswith("text/html"):
            html_text = flow.response.content
            if len(html_text) > 0:
                soup = BeautifulSoup(html_text, "html.parser")
                title = soup.title.string.strip()
                return f"{self.__clean_title(title)}"

    def save_content(self, flow: mitmproxy.http.HTTPFlow):
        for tag in self.soup.find_all(["img", "link", "script"]):
            url = tag.get("src") or tag.get("href")
            if url:
                full_url = urljoin(flow.request.url, url)
                self.save_resource(full_url)

    def save_resource(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            filename = f"{self.__clean_title(url)}"
            filepath = os.path.join(self.acq_dir, f"{self.filename_page}_files")
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            with open(os.path.join(filepath, filename), "wb") as f:
                f.write(response.content)

    def __clean_title(self, name):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        cleaned_title = "".join(
            c if c in valid_chars else "-" for c in os.path.basename(name)
        )
        return cleaned_title
