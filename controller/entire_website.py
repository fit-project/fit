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

from controller.configurations.tabs.general.general import (
    General as GeneralConfigurationController,
)
from common.utility import get_version


class EntireWebsite:
    def __init__(self):
        self.url = None
        self.acquisition_dir = None
        user_agent = GeneralConfigurationController().configuration.get("user_agent")
        user_agent + " FreezingInternetTool/" + get_version()
        self.headers = {"User-Agent": user_agent}

    def set_url(self, url):
        self.url = url

    def is_valid_url(self, url):
        requests.get(url, headers=self.headers)

    def set_dir(self, acquisition_dir):
        self.acquisition_dir = acquisition_dir

    def set_proxy(self, port):
        self.proxy_dict = {
            "http": f"http://127.0.0.1:{port}",
            "https": f"http://127.0.0.1:{port}",
        }

    def download(self, url):
        requests.get(url, proxies=self.proxy_dict, verify=False, headers=self.headers)

    def get_sitemap(self):
        # check if /sitemap exists
        sitemap_candidate = self.url + "/sitemap/"
        response = requests.get(sitemap_candidate, headers=self.headers)
        if response.status_code == 200:
            return self.__crawl_links(response)

        else:  # else, search for sitemap link inside the html
            response = requests.get(self.url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                sitemaps = soup.find_all("link", rel="sitemap")
                if sitemaps:
                    for sitemap in sitemaps:
                        response = requests.get(sitemap["href"], headers=self.headers)
                        if response.status_code == 200:
                            return self.__crawl_links(response)
                else:
                    # crawl manually from the url
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
