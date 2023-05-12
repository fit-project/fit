#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

import logging
from PyQt5 import QtCore

from common.utility import get_headers_information
from common.constants import logger as Logger, state, status, tasks

from view.acquisition.tasks.task import AcquisitionTask



logger = logging.getLogger('headers')

class AcquisitionHeaders(AcquisitionTask):

    def __init__(self, name, state, status, parent: None):
        super().__init__(name, state, status, parent)

    def start(self, url):

        logger.info(get_headers_information(url))
        self.parent().logger.info(Logger.HEADERS_GET)
        self.parent().task_is_completed({
                                'name' : tasks.HEADERS,
                                'state' : state.FINISHED,
                                'status' : status.COMPLETED
                                })
                            