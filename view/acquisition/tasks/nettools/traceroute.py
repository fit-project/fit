#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import os
from PyQt5 import QtCore

from common.utility import traceroute
from common.constants import logger as Logger, state, status, tasks

from view.acquisition.tasks.task import AcquisitionTask


class AcquisitionTraceroute(AcquisitionTask):

    def __init__(self, name, state, status, parent: None):
        super().__init__(name, state, status, parent)

    def start(self, url, folder):

        traceroute(url, os.path.join(folder, 'traceroute.txt'))
        
        self.parent().logger.info(Logger.TRACEROUTE_GET)
        self.parent().task_is_completed({
                                'name' : tasks.TRACEROUTE,
                                'state' : state.FINISHED,
                                'status' : status.COMPLETED
                            })
                            