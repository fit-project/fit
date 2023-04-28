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

import os
import logging
from PyQt5 import QtCore, QtWidgets

from common.constants import logger as Logger, details, state, status as Status, tasks, error
from common.utility import calculate_hash

from controller.report import Report as ReportController
from controller.configurations.tabs.timestamp.timestamp import Timestamp as TimestampController
from controller.configurations.tabs.pec.pec import Pec as PecController

from view.timestamp import Timestamp as TimestampView
from view.pec.pec import Pec as PecView
from view.error import Error as ErrorView

logger = logging.getLogger('hashreport')

class PostAcquisition(QtCore.QObject):
    def __init__(self, parent: None):
        super().__init__(parent)
    

    def execute(self, folder, case_info, type):
       self.calculate_acquisition_file_hash(folder)
       self.generate_pdf_report(folder, case_info, type)
       self.generate_timestamp_report(folder)
       self.send_report_from_pec(folder, case_info)
        
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

    #TODO is async?
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

    def send_report_from_pec(self, folder, case_info):

        self.parent().set_message_on_the_statusbar(tasks.PEC)

        options = PecController().options
        if options['enabled']:
            self.pec = PecView(self)
            self.pec.sentpec.connect(lambda status: self.__is_pec_sent(status))
            self.pec.downloadedeml.connect(lambda status: self.__is_eml_downloaded(status))
            view_form=True
            self.pec.init(case_info, "Web", folder, view_form)
            if view_form is False:
                self.pec.send()
                
    def __is_pec_sent(self, status):
        if status == Status.SUCCESS:
            self.pec.download_eml()
            self.parent().set_message_on_the_statusbar(tasks.EML)
    
    def __is_eml_downloaded(self, status):
       self.parent().upadate_progress_bar()
    
