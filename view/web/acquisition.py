#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from view.acquisition.acquisition import Acquisition
from view.tasks.class_names import *


class WebAcquisition(Acquisition):
    def __init__(self, options, logger, progress_bar, status_bar, parent=None):
        super().__init__(options, logger, progress_bar, status_bar, parent)

        self.start_tasks = [SCREENRECORDER, PACKETCAPTURE]
        self.stop_tasks = [
            WHOIS,
            NSLOOKUP,
            HEADERS,
            TRACEROUTE,
            SSLKEYLOG,
            SSLCERTIFICATE,
            PACKETCAPTURE,
            TAKE_FULL_PAGE_SCREENSHOT,
            SAVE_PAGE,
        ]
