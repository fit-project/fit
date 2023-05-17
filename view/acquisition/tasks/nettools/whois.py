#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import logging
from PyQt6 import QtCore

from common.utility import whois
from common.constants import logger as Logger, state, status, tasks

from view.acquisition.tasks.task import AcquisitionTask


logger = logging.getLogger('whois')

class AcquisitionWhois(AcquisitionTask):

    def __init__(self, name, state, status, parent: None):
        super().__init__(name, state, status, parent)

    def start(self, url):
        
        logger.info(whois(url))
        
        self.parent().logger.info(Logger.WHOIS_GET)
        self.parent().task_is_completed({
                                'name' : tasks.WHOIS,
                                'state' : state.FINISHED,
                                'status' : status.COMPLETED
                            })
                            