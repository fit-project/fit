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
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup


class EntireWebsite:
    def __init__(self):
        self.url = None
        self.id_digest = None

    def set_url(self, url):
        self.url = url
        self.id_digest = self.__calculate_md5()

    def create_zip(self, path):
        for folder in os.listdir(path):
            folder_path = os.path.join(path, folder)
            if os.path.isdir(folder_path):
                shutil.make_archive(folder_path, "zip", folder_path)
                shutil.rmtree(folder_path)

    def is_valid_url(self, url):
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            requests.get(url)

    def download(self):
        return

    def __calculate_md5(self):
        md5 = hashlib.md5()
        bytes = self.url.encode("utf-8")
        md5.update(bytes)
        md5_id = md5.hexdigest()
        return md5_id

    def check_sitemap(self):
        sitemap_candidate = self.url + '/sitemap/'
        response = requests.get(sitemap_candidate)
        if response.status_code == 200:
            return self.__crawl_links(response)

        else:
            response = requests.get(self.url)
            if requests.get(self.url) == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                sitemaps = soup.find_all('link', rel='sitemap')
                if sitemaps:
                    for sitemap in sitemaps:
                        response = requests.get(sitemap['href'])
                        if response.status_code == 200:
                            return self.__crawl_links(response)
            else:
                # crawl manually from the url
                response = requests.get(self.url)
                if response.status_code == 200:
                    self.__crawl_links(response)

    def __crawl_links(self, response):
        urls = set()
        soup = BeautifulSoup(response.content, 'html.parser')
        anchor_tags = soup.find_all('a')
        for tag in anchor_tags:
            href = tag.get('href')
            if href and not href.startswith('#'):
                absolute_url = urljoin(self.url, href)
                urls.add(absolute_url)
        return urls
