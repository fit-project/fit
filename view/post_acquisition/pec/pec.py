# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
#
# Copyright (c) 2022 FIT-Project and others
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
import imaplib
import os
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from view.post_acquisition.pec.pec_form import PecForm as PecFormView
from view.error import Error as ErrorView
from view.post_acquisition.pec.eml_not_found import EmlNotFound as EmlNotFoundView

from controller.pec import Pec as PecController
from controller.configurations.tabs.pec.pec import Pec as PecConfigController

from common.constants.view.pec import pec
from common.constants.status import *

class Pec(QtCore.QObject):

    sentpec = QtCore.pyqtSignal(str)
    downloadedeml = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pec_form = None
        self.pec_controller = None
        self.is_form_enable = False

        self.controller = PecConfigController()
        self.options = self.controller.options

    def init(self, case_info, acquisition_type, acquisition_directory, is_form_enable=False):
        self.case_info = case_info
        self.acquisition_type = acquisition_type
        self.acquisition_directory = acquisition_directory
        self.is_form_enable = is_form_enable

        if self.is_form_enable:
            self.pec_form = PecFormView(self)
            self.pec_form.exec_()

    
    def send(self):
        status = SUCCESS
        if len(self.options) == 0:
           return
        
        self.pec_controller = PecController(self.options.get('pec_email'), self.options.get('password'), self.acquisition_type,
                            self.case_info['name'], self.acquisition_directory, self.options.get('smtp_server'),
                            self.options.get('smtp_port'), self.options.get('imap_server'), self.options.get('imap_port'))
        try:
            self.pec_controller.send_pec()

            if self.is_form_enable:
                if self.pec_form.check_box_save_pec_configuration:
                    self.controller.options = self.options
                self.pec_form.progress_bar.setValue(50)
                self.pec_form.output_message.setText(pec.SEND_PEC_SUCCESS)

        except Exception as e:
            status = FAIL
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                    pec.LOGIN_FAILED,
                                    pec.SMTP_FAILED_MGS,
                                    str(e))
            error_dlg.exec_()

        if self.is_form_enable:
            self.pec_form.centralwidget.setDisabled(False)

        self.sentpec.emit(status)
        

    def download_eml(self):
        if len(self.options) == 0 or self.pec_controller is None:
           return
        
        if self.is_form_enable:
            self.pec_form.centralwidget.setDisabled(True)
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(500, loop.quit)
            loop.exec_()

        status = SUCCESS
        retries = self.options.get('retries')
        result = False

        if retries > 0:
            increment = 50/retries

        for i in range(self.options.get('retries')):
            if self.is_form_enable:
                self.pec_form.output_message.setText(pec.TRY_DOWNLOAD_EML.format(str(i + 1)))
                self.pec_form.progress_bar.setValue(self.pec_form.progress_bar.value() + increment)
            
            #whait for 8 seconds
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(8000, loop.quit)
            loop.exec_()

            try:
                result = self.pec_controller.retrieve_eml()
                if result:
                    break
            except Exception as e:
                status = FAIL
                error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                        pec.LOGIN_FAILED,
                                        pec.IMAP_FAILED_MGS,
                                        str(e))
                error_dlg.exec_()
                break

        if result:
            if self.is_form_enable:
                self.pec_form.progress_bar.setValue(100 - self.pec_form.progress_bar.value())
                self.pec_form.output_message.setText(pec.DOWNLOAD_EML_SUCCESS)
                self.pec_form.close()
            self.downloadedeml.emit(status)
        else:
            self.eml_not_found = EmlNotFoundView(self.acquisition_directory, self.case_info, self.options.get('retries'))
            self.eml_not_found.search.downloadedeml.connect(lambda status:self.downloadedeml.emit(status))
            self.eml_not_found.show()

            if self.is_form_enable:
                self.pec_form.close()