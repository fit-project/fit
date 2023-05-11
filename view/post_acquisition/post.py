#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

import os
import logging
from PyQt5 import QtCore, QtWidgets

from common.constants import logger as Logger, details, state, status as Status, tasks, error
from common.utility import calculate_hash

from controller.report import Report as ReportController
from controller.configurations.tabs.timestamp.timestamp import Timestamp as TimestampController
from controller.configurations.tabs.pec.pec import Pec as PecController

from view.post_acquisition.timestamp import Timestamp as TimestampView
from view.post_acquisition.pec.pec import Pec as PecView
from view.error import Error as ErrorView

logger = logging.getLogger('hashreport')

class PostAcquisition(QtCore.QObject):
    def __init__(self, parent: None):
        super().__init__(parent)
    

    def execute(self, folder, case_info, type):
       self.calculate_acquisition_file_hash(folder)
       self.generate_pdf_report(folder, case_info, type)
       self.generate_timestamp_report(folder)
       self.send_report_from_pec(folder, case_info, type)
        
    def calculate_acquisition_file_hash(self, folder):

        self.parent().set_message_on_the_statusbar(tasks.HASHFILE)

        files = [f.name for f in os.scandir(folder) if f.is_file()]
        for file in files:
            if file != 'acquisition.hash':
                filename = os.path.join(folder, file)
                file_stats = os.stat(filename)
                logger.info(file)
                logger.info('=========================================================')
                logger.info(f'Size: {file_stats.st_size}')
                algorithm = 'md5'
                logger.info(f'MD5: {calculate_hash(filename, algorithm)}')
                algorithm = 'sha1'
                logger.info(f'SHA-1: {calculate_hash(filename, algorithm)}')
                algorithm = 'sha256'
                logger.info(f'SHA-256: {calculate_hash(filename, algorithm)}\n')

        self.parent().upadate_progress_bar()

        
    def generate_pdf_report(self, folder, case_info,type):
        self.parent().set_message_on_the_statusbar(tasks.REPORTFILE)
        report = ReportController(folder, case_info)
        report.generate_pdf(type, self.parent().get_time())
        self.parent().upadate_progress_bar()

    def generate_timestamp_report(self, folder):
        self.parent().set_message_on_the_statusbar(tasks.TIMESTAMP)
        options = TimestampController().options
        if options['enabled']:
            timestamp = TimestampView()
            timestamp.set_options(options)
            try:
                timestamp.apply_timestamp(folder, 'acquisition_report.pdf')
            except Exception as e:
                error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                        tasks.TIMESTAMP,
                                        error.TIMESTAMP_TIMEOUT,
                                        "Error: %s - %s." % (e.filename, e.strerror)
                                        )

                error_dlg.buttonClicked.connect(quit)
        self.parent().upadate_progress_bar()

    def send_report_from_pec(self, folder, case_info, type):

        self.parent().set_message_on_the_statusbar(tasks.PEC)

        options = PecController().options
        if options['enabled']:
            self.pec = PecView(self)
            self.pec.sentpec.connect(lambda status: self.__is_pec_sent(status))
            self.pec.downloadedeml.connect(lambda status: self.__is_eml_downloaded(status))
            view_form=True
            self.pec.init(case_info, type, folder, view_form)
            if view_form is False:
                self.pec.send()
                
    def __is_pec_sent(self, status):
        if status == Status.SUCCESS:
            self.pec.download_eml()
            self.parent().set_message_on_the_statusbar(tasks.EML)
    
    def __is_eml_downloaded(self, status):
       self.parent().upadate_progress_bar()
    
