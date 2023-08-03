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


class EntireWebsite:
    def __init__(self):
        self.url = None
        self.id_digest = None

    def set_url(self, url):
        self.url = url

    def create_zip(self, path):
        for folder in os.listdir(path):
            folder_path = os.path.join(path, folder)
            if os.path.isdir(folder_path):
                shutil.make_archive(folder_path, "zip", folder_path)
                shutil.rmtree(folder_path)

    def set_id(self):
        self.id = self.__calculate_md5()

    def __calculate_md5(self):
        md5 = hashlib.md5()
        bytes = self.url.encode("utf-8")
        md5.update(bytes)
        md5_id = md5.hexdigest()
        return md5_id
