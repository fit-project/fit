#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  
import sslkeylog
import os
from PyQt6 import QtCore

from common.constants import logger as Logger, state, status, tasks

from view.acquisition.tasks.task import AcquisitionTask


class AcquisitionSSLKeyLog(AcquisitionTask):

    def __init__(self, name, state, status, parent: None):
        super().__init__(name, state, status, parent)

    def start(self, folder):

        sslkeylog.set_keylog(os.path.join(folder, 'sslkey.log'))
        
        self.parent().logger.info(Logger.SSLKEYLOG_GET)
        self.parent().task_is_completed({
                                'name' : tasks.SSLKEYLOG,
                                'state' : state.FINISHED,
                                'status' : status.COMPLETED
                            })
                            