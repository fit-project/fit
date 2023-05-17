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
from PyQt6 import QtCore, QtWidgets

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
    finished = QtCore.pyqtSignal()

    def __init__(self, parent: None):
        super().__init__(parent)
        self.is_finished_timestamp = False
        self.is_finished_pec = False

    def execute(self, folder, case_info, type):
       self.calculate_acquisition_file_hash(folder)
       self.generate_pdf_report(folder, case_info, type)
       self.generate_timestamp_report(folder, case_info, type)

        
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
                algorithm = 'sha256'
                logger.info(f'SHA-256: {calculate_hash(filename, algorithm)}\n')
                algorithm = 'sha512'
                logger.info(f'SHA-512: {calculate_hash(filename, algorithm)}\n')

        self.parent().upadate_progress_bar()

        
    def generate_pdf_report(self, folder, case_info,type):
        self.parent().set_message_on_the_statusbar(tasks.REPORTFILE)
        report = ReportController(folder, case_info)
        report.generate_pdf(type, self.parent().get_time())
        self.parent().upadate_progress_bar()

    def generate_timestamp_report(self, folder, case_info, type):
        self.parent().set_message_on_the_statusbar(tasks.TIMESTAMP)
        options = TimestampController().options
        if options['enabled']:
            self.thread_timestamp = QtCore.QThread()
            timestamp = TimestampView()
            timestamp.set_options(options)
            timestamp.moveToThread(self.thread_timestamp)
            self.thread_timestamp.started.connect(lambda: timestamp.apply_timestamp(folder, 'acquisition_report.pdf'))

            timestamp.finished.connect(timestamp.deleteLater)
            timestamp.finished.connect(self.thread_timestamp.quit)
            
            self.thread_timestamp.finished.connect(lambda:self.__thread_timestamp_is_finished(folder, case_info, type))

            self.thread_timestamp.start()
    
    def __thread_timestamp_is_finished(self,folder, case_info, type):
        options = PecController().options
        if options['enabled']:
            self.send_report_from_pec(folder, case_info, type)
        else:
            self.is_finished_pec = True
        self.parent().upadate_progress_bar()
        self.is_finished_timestamp = True
        self.__async_task_are_finished()

    def send_report_from_pec(self, folder, case_info, type):

        self.parent().set_message_on_the_statusbar(tasks.PEC)

        self.pec = PecView(self)
        self.pec.sentpec.connect(lambda status: self.__is_pec_sent(status))
        self.pec.downloadedeml.connect(lambda status: self.__is_eml_downloaded(status))
        view_form = False
        self.pec.init(case_info, type, folder, view_form)
        if view_form is False:
            self.pec.send()

                
    def __is_pec_sent(self, status):
        if status == Status.SUCCESS:
            self.pec.download_eml()
            self.parent().set_message_on_the_statusbar(tasks.EML)
        else:
            self.is_finished_pec = True
            self.__async_task_are_finished()
    
    def __is_eml_downloaded(self, status):
       self.parent().upadate_progress_bar()
       self.is_finished_pec = True
       self.__async_task_are_finished()

    def __async_task_are_finished(self):
        if self.is_finished_timestamp and self.is_finished_pec:
            self.finished.emit()
    
