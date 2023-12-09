#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
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

    def create_folders(self, flow: mitmproxy.http.HTTPFlow):
        if flow.response.headers.get("content-type", "").startswith("text/html"):
            self.html_text = flow.response.content
            if len(self.html_text) > 0:
                soup = BeautifulSoup(self.html_text, "html.parser")
                self.title = soup.title.string.strip()
                self.clean_title = self.__clean_title(self.title)
                self.clean_title_path = os.path.join(
                    self.acq_dir, f"{self.clean_title}_files"
                )

                if not os.path.exists(self.clean_title_path):
                    os.makedirs(self.clean_title_path)

    def save_resources(self, flow: mitmproxy.http.HTTPFlow):
        # save resources in separate threads
        self.save_html()
        resources_thread = threading.Thread(target=self.save_content, args=(flow,))
        resources_thread.start()
        resources_thread.join()

    def save_html(self):
        with open(f"{self.acq_dir}/{self.clean_title}.html", "wb") as f:
            f.write(self.html_text)

    def save_content(self, flow: mitmproxy.http.HTTPFlow):
        soup = BeautifulSoup(self.html_text, "html.parser")
        for tag in soup.find_all(["img", "link", "script"]):
            url = tag.get("src") or tag.get("href")
            if url:
                full_url = urljoin(flow.request.url, url)
                self.save_resource(full_url)

    def save_resource(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            filename = f"{self.__clean_title(url)}"
            try:
                with open(os.path.join(self.clean_title_path, filename), "wb") as f:
                    f.write(response.content)
            except:
                pass  # check

    def __clean_title(self, name):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        cleaned_title = "".join(
            c if c in valid_chars else "-" for c in os.path.basename(name)
        )
        return cleaned_title
