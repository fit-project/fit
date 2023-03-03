#!/usr/bin/env python3
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
import hashlib
import os

import rfc3161ng

import common.utility as utility
from view.error import Error as ErrorView
from view.configuration import Configuration as ConfigurationView

from controller.verify_pdf_timestamp import VerifyPDFTimestamp as VerifyPDFTimestampController

from common.error import ErrorMessage

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog


class VerifyPDFTimestamp(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(VerifyPDFTimestamp, self).__init__(*args, **kwargs)

        self.data = None  # acquisition_report.pdf
        self.tsr_in = None  # timestamp.tsr
        self.untrusted = None  # tsa.crt
        self.error_msg = ErrorMessage()
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()

    def init(self, case_info, acquisition_directory=None):
        self.width = 690
        self.height = 250
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info
        self.acquisition_directory = acquisition_directory

        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))
        self.setObjectName("verify_timestamp_window")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("QWidget {background-color: rgb(255, 255, 255);}")
        self.setCentralWidget(self.centralwidget)

        # set font
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily('Arial')

        # TIMESTAMP GROUP
        self.timestamp_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.timestamp_group_box.setEnabled(True)
        self.timestamp_group_box.setGeometry(QtCore.QRect(50, 20, 590, 200))
        self.timestamp_group_box.setObjectName("timestamp_group_box")

        # PDF FIELD
        self.input_pdf = QtWidgets.QLineEdit(self.centralwidget)
        self.input_pdf.setGeometry(QtCore.QRect(215, 60, 300, 20))
        self.input_pdf.setFont(QFont('Arial', 10))
        self.input_pdf.setObjectName("input_pdf")
        self.input_pdf.setEnabled(False)
        self.input_pdf_button = QtWidgets.QPushButton(self.centralwidget)
        self.input_pdf_button.setGeometry(QtCore.QRect(515, 60, 75, 20))
        self.input_pdf_button.setFont(font)
        self.input_pdf_button.clicked.connect(lambda extension: self.dialog('pdf'))

        # TSR FIELD
        self.input_tsr = QtWidgets.QLineEdit(self.centralwidget)
        self.input_tsr.setGeometry(QtCore.QRect(215, 95, 300, 20))
        self.input_tsr.setFont(QFont('Arial', 10))
        self.input_tsr.setObjectName("input_tsr")
        self.input_tsr.setEnabled(False)
        self.input_tsr_button = QtWidgets.QPushButton(self.centralwidget)
        self.input_tsr_button.setGeometry(QtCore.QRect(515, 95, 75, 20))
        self.input_tsr_button.setFont(font)
        self.input_tsr_button.clicked.connect(lambda extension: self.dialog('tsr'))

        # CRT FIELD
        self.input_crt = QtWidgets.QLineEdit(self.centralwidget)
        self.input_crt.setGeometry(QtCore.QRect(215, 130, 300, 20))
        self.input_crt.setFont(QFont('Arial', 10))
        self.input_crt.setObjectName("input_crt")
        self.input_crt.setEnabled(False)
        self.input_crt_button = QtWidgets.QPushButton(self.centralwidget)
        self.input_crt_button.setGeometry(QtCore.QRect(515, 130, 75, 20))
        self.input_crt_button.setFont(font)
        self.input_crt_button.clicked.connect(lambda extension: self.dialog('crt'))

        # PDF LABEL
        self.label_pdf = QtWidgets.QLabel(self.centralwidget)
        self.label_pdf.setGeometry(QtCore.QRect(90, 60, 120, 20))
        self.label_pdf.setFont(font)
        self.label_pdf.setAlignment(QtCore.Qt.AlignRight)
        self.label_pdf.setObjectName("label_pdf")

        # TSR LABEL
        self.label_tsr = QtWidgets.QLabel(self.centralwidget)
        self.label_tsr.setGeometry(QtCore.QRect(90, 95, 120, 20))
        self.label_tsr.setFont(font)
        self.label_tsr.setAlignment(QtCore.Qt.AlignRight)
        self.label_tsr.setObjectName("label_tsr")

        # CRT LABEL
        self.label_crt = QtWidgets.QLabel(self.centralwidget)
        self.label_crt.setGeometry(QtCore.QRect(90, 130, 120, 20))
        self.label_crt.setFont(font)
        self.label_crt.setAlignment(QtCore.Qt.AlignRight)
        self.label_crt.setObjectName("label_crt")

        # VERIFICATION BUTTON
        self.verification_button = QtWidgets.QPushButton(self.centralwidget)
        self.verification_button.setGeometry(QtCore.QRect(300, 170, 75, 30))
        self.verification_button.clicked.connect(self.verify)
        self.verification_button.setFont(font)
        self.verification_button.setObjectName("StartAction")
        self.verification_button.setEnabled(False)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_pdf, self.input_tsr, self.input_crt]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.onTextChanged)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("verify_timestamp_window", "Freezing Internet Tool"))
        self.timestamp_group_box.setTitle(_translate("verify_timestamp_window", "Impostazioni timestamp"))
        self.label_pdf.setText(_translate("verify_timestamp_window", "Report (.pdf)"))
        self.label_tsr.setText(_translate("verify_timestamp_window", "Timestamp (.tsr)"))
        self.label_crt.setText(_translate("verify_timestamp_window", "TSA Certificate (.crt)"))
        self.verification_button.setText(_translate("verify_timestamp_window", "Verify"))
        self.input_pdf_button.setText(_translate("verify_timestamp_window", "Browse..."))
        self.input_tsr_button.setText(_translate("verify_timestamp_window", "Browse..."))
        self.input_crt_button.setText(_translate("verify_timestamp_window", "Browse..."))

    def verify(self):

        tsr_in = self.input_tsr.text()
        untrusted = self.input_crt.text()
        data = self.input_pdf.text()

        certificate = open(untrusted, 'rb').read()
        configuration_timestamp = self.configuration_view.get_tab_from_name("configuration_timestamp")
        options = configuration_timestamp.options
        server_name = options['server_name']

        # verify timestamp
        rt = rfc3161ng.RemoteTimestamper(server_name, certificate=certificate, hashname='sha256')
        timestamp = open(tsr_in, 'rb').read()

        try:
            verified = rt.check(timestamp, data=open(data, 'rb').read())

            report, info_file_path = self.generate_report_verification(data, rt, server_name, timestamp, True)
            if verified:  # it's called ErrorView but it's an informative message :(

                report.generate_pdf(True, info_file_path)

                error_dlg = ErrorView(QtWidgets.QMessageBox.Information,
                                      self.error_msg.TITLES['verification_ok'],
                                      self.error_msg.MESSAGES['verification_ok'],
                                      "PDF has a valid timestamp, report has been generated.")
                error_dlg.exec_()


        except Exception:
            # timestamp not validated

            report, info_file_path = self.generate_report_verification(data, rt, server_name, timestamp, False)
            report.generate_pdf(False, info_file_path)

            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  self.error_msg.TITLES['verification_failed'],
                                  self.error_msg.MESSAGES['verification_failed'],
                                  "PDF may have been tampered with, report has been generated.")
            error_dlg.exec_()

        folder = self.get_current_dir()
        os.startfile(folder)
        return

    def onTextChanged(self):
        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.verification_button.setEnabled(all_fields_filled)

    def dialog(self, extension):
        # open the correct file picker based on extension
        open_folder = self.get_current_dir()

        if extension == 'pdf':
            file, check = QFileDialog.getOpenFileName(None, "Open PDF",
                                                      open_folder, "PDF Files (*.pdf)")
            if check:
                self.input_pdf.setText(file)
        elif extension == 'tsr':
            file, check = QFileDialog.getOpenFileName(None, "Open timestamp",
                                                      open_folder, "TSR Files (*.tsr)")
            if check:
                self.input_tsr.setText(file)

        elif extension == 'crt':
            file, check = QFileDialog.getOpenFileName(None, "Open certificate",
                                                      open_folder, "CERT Files (*.crt)")
            if check:
                self.input_crt.setText(file)

    def generate_report_verification(self, data, rt, server_name, timestamp, check):
        folder = self.get_current_dir()

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")
        self.configuration_network = self.configuration_general.findChild(QtWidgets.QGroupBox,
                                                                          'group_box_network_check')
        ntp = utility.get_ntp_date_and_time(self.configuration_network.configuration["ntp_server"])

        if check:
            verification = 'Il report ha un timestamp valido'
        else:
            verification = 'Il report non ha un timestamp valido'

        # calculate hash (as in rfc lib)
        hashobj = hashlib.new('sha256')
        hashobj.update(open(data, 'rb').read())
        digest = hashobj.hexdigest()

        # get date from tsr file
        timestamp_datetime = rfc3161ng.get_timestamp(timestamp)

        info_file_path = f'{folder}/timestamp_info.txt'
        with open(info_file_path, 'w') as file:

            file.write('======================================================================\n')
            file.write(f'ESITO\n')
            file.write(f'{verification}\n')
            file.write('======================================================================\n')
            file.write(f'NOME DEL FILE\n')
            file.write(f'{os.path.basename(self.input_pdf.text())}\n')
            file.write('======================================================================\n')
            file.write(f'DIMENSIONE\n')
            file.write(f'{os.path.getsize(self.input_pdf.text())} bytes\n')
            file.write('======================================================================\n')
            file.write(f'ALGORITMO DI HASHING\n')
            file.write('sha-256\n')
            file.write('======================================================================\n')
            file.write(f'DIGEST\n')
            file.write(f'{digest}\n')
            file.write('======================================================================\n')
            file.write(f'TIMESTAMP\n')
            file.write(f'{str(timestamp_datetime)}\n')
            file.write('======================================================================\n')
            file.write(f'SERVER\n')
            file.write(f'{server_name}\n')
            file.write('======================================================================\n')

        report = VerifyPDFTimestampController(folder, self.case_info, ntp)
        return report, info_file_path

    def get_current_dir(self):
        if not self.acquisition_directory:
            configuration_general = self.configuration_view.get_tab_from_name("configuration_general")
            open_folder = os.path.expanduser(
                os.path.join(configuration_general.configuration['cases_folder_path'], self.case_info['name']))
            return open_folder
        else:
            return self.acquisition_directory
