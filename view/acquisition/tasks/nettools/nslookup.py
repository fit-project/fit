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

from common.utility import nslookup
from common.constants import logger as Logger, state, status, tasks

from view.acquisition.tasks.task import AcquisitionTask


logger = logging.getLogger('nslookup')

class AcquisitionNslookup(AcquisitionTask):

    def __init__(self, name, state, status, parent: None):
        super().__init__(name, state, status, parent)

    def start(self, url, configuration):

        logger.info(nslookup(url,
                configuration["nslookup_dns_server"],
                configuration["nslookup_enable_tcp"],
                configuration["nslookup_enable_verbose_mode"]
                ))
        
        self.parent().logger.info(Logger.NSLOOKUP_GET)
        self.parent().task_is_completed({
                                'name' : tasks.NSLOOKUP,
                                'state' : state.FINISHED,
                                'status' : status.COMPLETED
                            })