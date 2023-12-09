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


class EntireWebsiteUrlWorker(QObject):
    valid_url = pyqtSignal(str)
    error = pyqtSignal(object)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def check(self):
        controller = self.options.get("entire_website_controller")
        __status = status.SUCCESS

        try:
            controller.is_valid_url(self.options.get("url"))

        except Exception as e:
            __status = status.FAIL
            self.error.emit(
                {
                    "title": entire_site.INVALID_URL,
                    "msg": error.INVALID_URL,
                    "details": str(e),
                }
            )

        self.valid_url.emit(__status)
