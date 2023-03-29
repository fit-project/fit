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
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog

from common import utility
from controller.integrityPec.verifyPec import verifyPec as verifyPecController
from common.error import ErrorMessage
from view.configuration import Configuration as ConfigurationView


class VerifyPec(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(VerifyPec, self).__init__(*args, **kwargs)
        self.data = None  # file .eml
        self.error_msg = ErrorMessage()
        self.configuration_view = ConfigurationView(self)

    def init(self, case_info):
        self.width = 600
        self.height = 230
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info

        self.setWindowIcon(QtGui.QIcon(os.path.join('assets/images/', 'icon.png')))
        self.setObjectName("verify_pec_window")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("QWidget {background-color: rgb(255, 255, 255);}")
        self.setCentralWidget(self.centralwidget)

        self.eml_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.eml_group_box.setEnabled(True)
        self.eml_group_box.setGeometry(QtCore.QRect(50, 20, 500, 180))
        self.eml_group_box.setObjectName("eml_group_box")

        # EML
        self.input_eml = QtWidgets.QLineEdit(self.centralwidget)
        self.input_eml.setGeometry(QtCore.QRect(160, 60, 260, 20))
        self.input_eml.setObjectName("input_eml")
        self.input_eml.setEnabled(False)
        self.input_eml_button = QtWidgets.QPushButton(self.centralwidget)
        self.input_eml_button.setGeometry(QtCore.QRect(450, 60, 75, 20))
        self.input_eml_button.clicked.connect(lambda extension: self.dialog('eml'))

        # EML LABEL
        self.label_eml = QtWidgets.QLabel(self.centralwidget)
        self.label_eml.setGeometry(QtCore.QRect(80, 60, 50, 20))
        self.label_eml.setAlignment(QtCore.Qt.AlignRight)
        self.label_eml.setObjectName("label_eml")

        # VERIFICATION BUTTON
        self.verification_button = QtWidgets.QPushButton(self.centralwidget)
        self.verification_button.setGeometry(QtCore.QRect(450, 140, 75, 30))
        self.verification_button.clicked.connect(self.verify)
        self.verification_button.setObjectName("StartAction")
        self.verification_button.setEnabled(False)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_eml]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.onTextChanged)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("verify_eml_window", "Freezing Internet Tool"))
        self.eml_group_box.setTitle(_translate("verify_eml_window", "Impostazioni eml"))
        self.label_eml.setText(_translate("verify_eml_window", "EML File (.eml)"))
        self.verification_button.setText(_translate("verify_eml_window", "Verify"))
        self.input_eml_button.setText(_translate("verify_timestamp_window", "Browse..."))

    def onTextChanged(self):
        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.verification_button.setEnabled(all_fields_filled)

    def verify(self):
        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")
        # Get network parameters for check (NTP, nslookup)
        self.configuration_network = self.configuration_general.findChild(QtWidgets.QGroupBox,
                                                                          'group_box_network_check')
        ntp = utility.get_ntp_date_and_time(self.configuration_network.configuration["ntp_server"])
        pec = verifyPecController()
        pec.verifyPec(self.input_eml.text(), self.case_info, ntp)
        path = os.path.dirname(str(self.input_eml.text()))
        os.startfile(path)
        self.close()

    def dialog(self, extension):
        # open the correct file picker based on extension
        if extension == 'eml':
            file, check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                                      "", "EML Files (*.eml)")
            if check:
                self.input_eml.setText(file)

