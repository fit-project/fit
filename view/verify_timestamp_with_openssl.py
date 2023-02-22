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
import os
import subprocess


from view.error import Error as ErrorView
from common.error import ErrorMessage

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog


class VerifyTimestampWithOpenssl(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(VerifyTimestampWithOpenssl, self).__init__(*args, **kwargs)

        self.data = None  # acquisition_report.pdf
        self.tsr_in = None  # timestamp.tsr
        self.CAfile = None  # cacert.pem
        self.untrusted = None  # tsa.crt
        self.error_msg = ErrorMessage()

    def init(self, case_info):
        self.width = 690
        self.height = 300
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info

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
        self.timestamp_group_box.setGeometry(QtCore.QRect(50, 20, 590, 250))
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

        # PEM FIELD
        self.input_pem = QtWidgets.QLineEdit(self.centralwidget)
        self.input_pem.setGeometry(QtCore.QRect(215, 165, 300, 20))
        self.input_pem.setFont(QFont('Arial', 10))
        self.input_pem.setObjectName("input_pem")
        self.input_pem.setEnabled(False)
        self.input_pem_button = QtWidgets.QPushButton(self.centralwidget)
        self.input_pem_button.setGeometry(QtCore.QRect(515, 165, 75, 20))
        self.input_pem_button.setFont(font)
        self.input_pem_button.clicked.connect(lambda extension: self.dialog('pem'))

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

        # PEM LABEL
        self.label_pem = QtWidgets.QLabel(self.centralwidget)
        self.label_pem.setGeometry(QtCore.QRect(90, 165, 120, 20))
        self.label_pem.setFont(font)
        self.label_pem.setAlignment(QtCore.Qt.AlignRight)
        self.label_pem.setObjectName("label_pem")

        # VERIFICATION BUTTON
        self.verification_button = QtWidgets.QPushButton(self.centralwidget)
        self.verification_button.setGeometry(QtCore.QRect(500, 210, 75, 30))
        self.verification_button.clicked.connect(self.verify)
        self.verification_button.setFont(font)
        self.verification_button.setObjectName("StartAction")
        self.verification_button.setEnabled(False)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_pdf, self.input_tsr, self.input_crt, self.input_pem]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.onTextChanged)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("verify_timestamp_window", "Freezing Internet Tool"))
        self.timestamp_group_box.setTitle(_translate("verify_timestamp_window", "Impostazioni timestamp"))
        self.label_pdf.setText(_translate("verify_timestamp_window", "Report (.pdf)"))
        self.label_tsr.setText(_translate("verify_timestamp_window", "Timestamp (.tsr)"))
        self.label_crt.setText(_translate("verify_timestamp_window", "TSA Certificate (.crt)"))
        self.label_pem.setText(_translate("verify_timestamp_window", "CA Certificate (.pem)"))
        self.verification_button.setText(_translate("verify_timestamp_window", "Verify"))
        self.input_pdf_button.setText(_translate("verify_timestamp_window", "Browse..."))
        self.input_tsr_button.setText(_translate("verify_timestamp_window", "Browse..."))
        self.input_crt_button.setText(_translate("verify_timestamp_window", "Browse..."))
        self.input_pem_button.setText(_translate("verify_timestamp_window", "Browse..."))

    def verify(self):
        CAfile = self.input_pem.text()
        tsr_in = self.input_tsr.text()
        untrusted = self.input_crt.text()
        data = self.input_pdf.text()
        print(os.environ["OPENSSL_PATH"])

        cmd = f'openssl ts -verify -data {data} -in {tsr_in} -CAfile {CAfile} -untrusted {untrusted}'

        output = subprocess.call(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE,  # 0 = verified, 1 = unverified
                                 stderr=subprocess.PIPE,
                                 shell=True)
        if output == 1:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  self.error_msg.TITLES['verification_failed'],
                                  self.error_msg.MESSAGES['verification_failed'],
                                  "PDF may have been tampered with.")
            error_dlg.exec_()

        if output == 0:  # it's called errorview but it's an informative message :(
            error_dlg = ErrorView(QtWidgets.QMessageBox.Information,
                                  self.error_msg.TITLES['verification_ok'],
                                  self.error_msg.MESSAGES['verification_ok'],
                                  "PDF has a valid timestamp.")
            error_dlg.exec_()
        return

    def onTextChanged(self):
        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.verification_button.setEnabled(all_fields_filled)

    def dialog(self, extension):
        # open the correct file picker based on extension
        if extension == 'pdf':
            file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                                      "", "PDF Files (*.pdf)")
            if check:
                self.input_pdf.setText(file)
        elif extension == 'tsr':
            file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                                      "", "TSR Files (*.tsr)")
            if check:
                self.input_tsr.setText(file)

        elif extension == 'crt':
            file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                                      "", "CERT Files (*.crt)")
            if check:
                self.input_crt.setText(file)
        elif extension == 'pem':
            file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                                      "", "PEM Files (*.pem)")
            if check:
                self.input_pem.setText(file)

