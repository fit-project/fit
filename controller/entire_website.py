#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import hashlib
import os
import shutil
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class EntireWebsite:
    def __init__(self):
        self.url = None
        self.acquisition_dir = None

    def set_url(self, url):
        self.url = url

    def is_valid_url(self, url):
        requests.get(url)

    def set_dir(self, acquisition_dir):
        self.acquisition_dir = acquisition_dir

    def set_proxy(self, port):
        self.proxy_dict = {
            "http": f"http://127.0.0.1:{port}",
            "https": f"http://127.0.0.1:{port}",
        }

    def download(self, url):
        requests.get(url, proxies=self.proxy_dict, verify=False)

    def check_sitemap(self):
        # check if /sitemap exists
        sitemap_candidate = self.url + "/sitemap/"
        response = requests.get(sitemap_candidate)
        if response.status_code == 200:
            return self.__crawl_links(response)

        else:  # else, search for sitemap link inside the html
            response = requests.get(self.url)
            if requests.get(self.url) == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                sitemaps = soup.find_all("link", rel="sitemap")
                if sitemaps:
                    for sitemap in sitemaps:
                        response = requests.get(sitemap["href"])
                        if response.status_code == 200:
                            return self.__crawl_links(response)
            else:
                # crawl manually from the url
                response = requests.get(self.url)
                if response.status_code == 200:
                    return self.__crawl_links(response)

    def __crawl_links(self, response):
        self.urls = set()
        soup = BeautifulSoup(response.content, "html.parser")
        anchor_tags = soup.find_all("a")
        self.urls.add(self.url)
        for tag in anchor_tags:
            href = tag.get("href")
            if href and not href.startswith("#"):
                absolute_url = urljoin(self.url, href)
                self.urls.add(absolute_url)
        return self.urls
