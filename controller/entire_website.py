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
        self.load_type = "load_from_domain"
        self.acquisition_dir = None
        user_agent = GeneralConfigurationController().configuration.get("user_agent")
        user_agent + " FreezingInternetTool/" + get_version()
        self.headers = {"User-Agent": user_agent}

    def set_url(self, url):
        self.url = url

    def set_load_type(self, load_type):
        self.load_type = load_type

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
        urls = set()

        if self.load_type == "load_from_domain":
            # check if /sitemap exists
            sitemap_candidate = self.url + "/sitemap/"
            response = requests.get(sitemap_candidate, headers=self.headers)
            if response.status_code == 200 and "text/html" in response.headers.get(
                "content-type"
            ):
                urls = self.__crawl_links(response)

            else:  # else, search for sitemap link inside the html
                response = requests.get(self.url, headers=self.headers)
                if response.status_code == 200 and "text/html" in response.headers.get(
                    "content-type"
                ):
                    soup = BeautifulSoup(response.content, "html.parser")
                    sitemaps = soup.find_all("link", rel="sitemap")
                    if sitemaps:
                        for sitemap in sitemaps:
                            response = requests.get(
                                sitemap["href"], headers=self.headers
                            )
                            if response.status_code == 200:
                                urls = self.__crawl_links(response)
                    else:
                        # crawl manually from the url
                        urls = self.__crawl_links(response)

        elif self.load_type == "load_from_sitemap":
            urls = self.__parse_sitemap(self.url)

        return urls

    def __crawl_links(self, response):
        urls = set()
        soup = BeautifulSoup(response.content, "html.parser")
        anchor_tags = soup.find_all("a")
        urls.add(self.url)
        for tag in anchor_tags:
            href = tag.get("href")
            if href and not href.startswith("#"):
                absolute_url = urljoin(self.url, href)
                urls.add(absolute_url)
        return urls

    def __parse_sitemap(self, url):
        urls = set()

        response = requests.get(url, headers=self.headers)
        if response.status_code == 200 and "text/xml" in response.headers.get(
            "content-type"
        ):
            soup = BeautifulSoup(response.content, features="xml")
            __urls = soup.findAll("url")

            if __urls:
                for u in __urls:
                    urls.add(u.find("loc").string)

        return urls
