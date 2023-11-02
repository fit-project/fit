#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import logging.config
from controller.configurations.tabs.network.networkcheck import NetworkControllerCheck


from common.utility import get_ntp_date_and_time
from common.config import LogConfigTools

from common.constants import logger


class Acquisition:
    def __init__(self, logger, folder):
        self.folder = folder
        self.logger = logger
        self.log_confing = LogConfigTools()

        if self.logger.name == "view.web.web":
            self.log_confing.set_dynamic_loggers()

        self.log_confing.change_filehandlers_path(self.folder)
        logging.config.dictConfig(self.log_confing.config)

    def start(self):
        self.log_start_message()

    def stop(self):
        self.log_stop_message()

    def log_start_message(self):
        self.logger.info(logger.ACQUISITION_STARTED)
        self.logger.info(logger.NTP_ACQUISITION_TIME.format("start", self.get_time()))

    def log_stop_message(self):
        self.logger.info(logger.ACQUISITION_STOPPED)
        self.logger.info(logger.NTP_ACQUISITION_TIME.format("stop", self.get_time()))

    def log_end_message(self):
        self.logger.info(logger.ACQUISITION_FINISHED)
        self.logger.info(logger.NTP_ACQUISITION_TIME.format("stop", self.get_time()))

    def get_time(self):
        return get_ntp_date_and_time(
            NetworkControllerCheck().configuration["ntp_server"]
        )

    def calculate_increment(self, tasks):
        return 100 / tasks
