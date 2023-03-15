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

from view.searchPec import SearchPec as SearchPecView


class EmlNotFound(QtWidgets.QMainWindow):
    def init(self, directory, case_info):

        self.directory = directory
        self.case_info = case_info

        self.setObjectName("mainWindow")
        self.resize(341, 153)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.scrapeButton = QtWidgets.QPushButton(self.centralwidget)
        self.scrapeButton.setGeometry(QtCore.QRect(40, 80, 111, 31))
        self.scrapeButton.setObjectName("scrapeButton")
        self.scrapeButton.clicked.connect(self.skip_search)
        self.scrapeButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.scrapeButton_2.setGeometry(QtCore.QRect(200, 80, 111, 31))
        self.scrapeButton_2.setObjectName("scrapeButton_2")
        self.scrapeButton_2.clicked.connect(self.manual_search)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 30, 251, 21))
        self.label.setObjectName("label")
        self.setCentralWidget(self.centralwidget)
        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "Freezing Internet Tool"))
        self.scrapeButton.setText(_translate("mainWindow", "Salta"))
        self.scrapeButton_2.setText(_translate("mainWindow", "Download Manuale"))
        self.label.setText(_translate("mainWindow", "Download file .eml fallito, PEC inviata correttamente"))

    def skip_search(self):
        os.startfile(str(self.directory))
        self.close()


    def manual_search(self):
        self.manualSearch = SearchPecView()
        self.manualSearch.hide()
        self.acquisition_window = self.manualSearch
        self.acquisition_window.init(self.case_info)
        self.acquisition_window.show()
        self.close()


