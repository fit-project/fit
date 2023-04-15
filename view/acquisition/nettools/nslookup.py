#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
# 
# Copyright (c) 2023 FIT-Project and others
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
###### 
import logging
from PyQt5 import QtCore

from common.utility import nslookup
from common.constants import logger as Logger, state, status, tasks

from view.acquisition.task import AcquisitionTask


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