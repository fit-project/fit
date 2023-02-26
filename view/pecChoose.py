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

from PyQt5 import QtCore, QtGui, QtWidgets
from view.verify_pec import VerifyPec as VerifyPecView
from view.searchPec import SearchPec as SearchPecView


class PecChoose(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(PecChoose, self).__init__(*args, **kwargs)

    def init(self, case_info):
        self.case_info = case_info
        self.setObjectName("mainWindow")
        self.resize(280, 96)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.scrapeButton = QtWidgets.QPushButton(self.centralwidget)
        self.scrapeButton.setGeometry(QtCore.QRect(20, 30, 101, 31))
        self.scrapeButton.setObjectName("scrapeButton")
        self.scrapeButton.clicked.connect(self.emlUpload)
        self.scrapeButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.scrapeButton_2.setGeometry(QtCore.QRect(160, 30, 91, 31))
        self.scrapeButton_2.setObjectName("scrapeButton_2")
        self.scrapeButton_2.clicked.connect(self.pecChoose)
        self.setCentralWidget(self.centralwidget)

        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("mainWindow", "Freezing Internet Tool"))
        self.scrapeButton.setText(_translate("mainWindow", "Upload file .eml"))
        self.scrapeButton_2.setText(_translate("mainWindow", "Search PEC"))

    def emlUpload(self):
        self.pec = VerifyPecView()
        self.pec.hide()
        self.acquisition_window = self.pec
        self.acquisition_window.init(self.case_info)
        self.acquisition_window.show()

    def pecChoose(self):
        self.searchPec = SearchPecView()
        self.searchPec.hide()
        self.acquisition_window = self.searchPec
        self.acquisition_window.init(self.case_info)
        self.acquisition_window.show()
