#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6.QtCore import QObject, pyqtSignal
from common.constants.view.tasks import status

from common.constants.view import entire_site
from common.constants import error


class EntireWebsiteSitemapWorker(QObject):
    sitemap = pyqtSignal(str, set)
    error = pyqtSignal(object)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def get_sitemap(self):
        controller = self.options.get("entire_website_controller")
        __status = status.SUCCESS
        urls = set()
        try:
            controller.set_url(self.options.get("url"))
            urls = controller.get_sitemap()

        except Exception as e:
            __status = status.FAIL
            self.error.emit(
                {
                    "title": entire_site.SITEMAP_ERROR,
                    "msg": error.SITEMAP_ERROR,
                    "details": str(e),
                }
            )

        self.sitemap.emit(__status, urls)
