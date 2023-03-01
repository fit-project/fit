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
from common.error import ErrorMessage
from view.acquisitionstatus import AcquisitionStatus as AcquisitionStatusView
from common.config import LogConfigMail
from view.configuration import Configuration as ConfigurationView
from view.case import Case as CaseView
from controller.pec import Pec as PecController
from controller.configurations.tabs.pec.pec import Pec as PecConfigController

class Pec(QtWidgets.QMainWindow):
    def case(self):
        self.case_view.exec_()

    def configuration(self):
        self.configuration_view.exec_()

    def _acquisition_status(self):
        self.acquisition_status.show()

    def __init__(self, *args, **kwargs):
        super(Pec, self).__init__(*args, **kwargs)
        self.error_msg = ErrorMessage()
        self.acquisition_directory = None
        self.acquisition_is_started = False
        self.acquisition_status = AcquisitionStatusView(self)
        self.acquisition_status.setupUi()
        self.log_confing = LogConfigMail()
        self.controller = PecConfigController()
        self.options = self.controller.options
        #aggiungere attributi per log, screencap ecc

    def init(self, case_info, acquisition, directory):
        self.case_info = case_info
        self.acquisition = acquisition
        self.directory = directory
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()
        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()
        self.setObjectName("mainWindow")
        self.resize(452, 333)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.input_username = QtWidgets.QLineEdit(self.centralwidget)
        self.input_username.setGeometry(QtCore.QRect(170, 30, 240, 20))
        self.input_username.setObjectName("input_username")
        self.input_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QtCore.QRect(170, 60, 240, 20))
        self.input_password.setObjectName("input_password")
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.label_username = QtWidgets.QLabel(self.centralwidget)
        self.label_username.setGeometry(QtCore.QRect(30, 30, 100, 20))
        self.label_username.setObjectName("label_username")
        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QtCore.QRect(30, 60, 100, 20))
        self.label_password.setObjectName("label_password")
        self.scrapeButton = QtWidgets.QPushButton(self.centralwidget)
        self.scrapeButton.setGeometry(QtCore.QRect(340, 230, 75, 25))
        self.scrapeButton.setObjectName("scrapeButton")
        self.scrapeButton.clicked.connect(self.button_clicked)
        self.scrapeButton.setEnabled(False)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(320, 280, 131, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)
        self.label_username_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_username_2.setGeometry(QtCore.QRect(30, 120, 100, 20))
        self.label_username_2.setObjectName("label_username_2")
        self.label_password_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_password_2.setGeometry(QtCore.QRect(30, 150, 100, 20))
        self.label_password_2.setObjectName("label_password_2")
        self.input_password_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password_2.setGeometry(QtCore.QRect(170, 150, 240, 20))
        self.input_password_2.setObjectName("input_password_2")
        self.input_username_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.input_username_2.setGeometry(QtCore.QRect(170, 120, 240, 20))
        self.input_username_2.setObjectName("input_username_2")

        # Verify if input fields are empty
        self.input_fields = [self.input_username, self.input_password, self.input_username_2, self.input_password_2]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.onTextChanged)

        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(170, 190, 111, 17))
        self.checkBox.setObjectName("checkBox")
        self.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 452, 21))
        self.menuBar.setObjectName("menuBar")
        self.menuConfiguration = QtWidgets.QMenu(self.menuBar)
        self.menuConfiguration.setObjectName("menuConfiguration")
        self.menuCase = QtWidgets.QMenu(self.menuBar)
        self.menuCase.setObjectName("menuCase")
        self.menuAcquisition = QtWidgets.QMenu(self.menuBar)
        self.menuAcquisition.setObjectName("menuAcquisition")
        self.setMenuBar(self.menuBar)
        self.menuBar.addAction(self.menuConfiguration.menuAction())
        self.menuBar.addAction(self.menuCase.menuAction())
        self.menuBar.addAction(self.menuAcquisition.menuAction())
        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))

        self.pecConfiguration = self.controller.get()
        if len(self.pecConfiguration) > 0:
            for pecConfig in self.pecConfiguration:
                self.input_username.setText(pecConfig.pec)
                self.input_password.setText(pecConfig.password)
                self.input_username_2.setText(pecConfig.server)
                self.input_password_2.setText(pecConfig.port)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("mainWindow", "Freezing Internet Tool"))
        self.label_username.setText(_translate("mainWindow", "Inserisci indirizzo PEC"))
        self.label_password.setText(_translate("mainWindow", "Inserisci la password"))
        self.scrapeButton.setText(_translate("mainWindow", "Invio"))
        self.label_username_2.setText(_translate("mainWindow", "Server"))
        self.label_password_2.setText(_translate("mainWindow", "Porta"))
        self.checkBox.setText(_translate("mainWindow", "Salva i miei dati"))
        self.menuConfiguration.setTitle(_translate("mainWindow", "Configuration"))
        self.menuCase.setTitle(_translate("mainWindow", "Case"))
        self.menuAcquisition.setTitle(_translate("mainWindow", "Acquisition"))

    def onTextChanged(self):
        all_field_filled = all(input_field.text() for input_field in self.input_fields)
        self.scrapeButton.setEnabled(all_field_filled)

    def button_clicked(self):
        self.progressBar.setValue(10)
        pec = PecController(self.input_username.text(), self.input_password.text(), self.acquisition,
                            self.case_info['name'], self.directory, self.input_username_2.text(),
                            self.input_password_2.text())
        self.progressBar.setValue(30)

        sendedPec = pec.sendPec()

        if sendedPec:
            pass
        else:
            if self.checkBox.isChecked():
                self.pecConfiguration = self.controller.get()
                if len(self.pecConfiguration) > 0:
                    for pecConfig in self.pecConfiguration:
                        pecConfigPec = pecConfig.pec
                        self.controller.delete(pecConfigPec)
                else:
                    pass
                self.controller.add(self.input_username.text(), self.input_password.text(), self.input_username_2.text(),
                                    self.input_password_2.text())


        self.progressBar.setValue(100)
        os.startfile(str(self.directory))
        if sendedPec:
            pass
        else:
            self.close()
