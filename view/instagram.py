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

from PyQt5 import QtCore, QtGui, QtWidgets
from controller.instagram import Instagram as InstragramController

class Instagram(QtWidgets.QMainWindow):
    insta = InstragramController()

    def __init__(self, *args, **kwargs):
        super(Instagram, self).__init__(*args, **kwargs)
        #aggiungere attributi per log, screencap ecc

    def init(self, case_info):
        self.setObjectName("mainWindow")
        self.resize(580, 311)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.input_username = QtWidgets.QLineEdit(self.centralwidget)
        self.input_username.setGeometry(QtCore.QRect(220, 30, 240, 20))
        self.input_username.setObjectName("input_username")
        self.input_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QtCore.QRect(220, 60, 240, 20))
        self.input_password.setObjectName("input_password")
        self.label_username = QtWidgets.QLabel(self.centralwidget)
        self.label_username.setGeometry(QtCore.QRect(60, 30, 100, 20))
        self.label_username.setObjectName("label_username")
        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QtCore.QRect(60, 60, 100, 20))
        self.label_password.setObjectName("label_password")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(440, 220, 75, 25))
        self.pushButton.setObjectName("pushButton")
        self.input_name = QtWidgets.QLineEdit(self.centralwidget)
        self.input_name.setGeometry(QtCore.QRect(220, 90, 240, 20))
        self.input_name.setText("")
        self.input_name.setObjectName("input_name")
        self.label_name = QtWidgets.QLabel(self.centralwidget)
        self.label_name.setGeometry(QtCore.QRect(60, 90, 141, 20))
        self.label_name.setObjectName("label_name")
        self.label_username_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_username_2.setGeometry(QtCore.QRect(60, 120, 111, 20))
        self.label_username_2.setObjectName("label_username_2")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(240, 150, 70, 17))
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setGeometry(QtCore.QRect(240, 170, 70, 17))
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3.setGeometry(QtCore.QRect(310, 170, 111, 17))
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_4 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_4.setGeometry(QtCore.QRect(310, 210, 70, 17))
        self.checkBox_4.setObjectName("checkBox_4")
        self.checkBox_5 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_5.setGeometry(QtCore.QRect(310, 190, 91, 17))
        self.checkBox_5.setObjectName("checkBox_5")
        self.checkBox_6 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_6.setGeometry(QtCore.QRect(310, 150, 91, 17))
        self.checkBox_6.setObjectName("checkBox_6")
        self.checkBox_7 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_7.setGeometry(QtCore.QRect(240, 190, 70, 17))
        self.checkBox_7.setObjectName("checkBox_7")
        self.label_username_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_username_3.setGeometry(QtCore.QRect(240, 120, 121, 20))
        self.label_username_3.setObjectName("label_username_3")
        self.label_username_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_username_4.setGeometry(QtCore.QRect(60, 150, 111, 20))
        self.label_username_4.setObjectName("label_username_4")
        self.label_username_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_username_5.setGeometry(QtCore.QRect(60, 170, 111, 20))
        self.label_username_5.setObjectName("label_username_5")
        self.label_username_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_username_6.setGeometry(QtCore.QRect(60, 190, 111, 20))
        self.label_username_6.setObjectName("label_username_6")
        self.label_username_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_username_7.setGeometry(QtCore.QRect(60, 210, 111, 20))
        self.label_username_7.setObjectName("label_username_7")
        self.label_username_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_username_8.setGeometry(QtCore.QRect(60, 230, 221, 20))
        self.label_username_8.setObjectName("label_username_8")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(450, 260, 118, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 580, 21))
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

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("mainWindow", "Freezing Internet Tool"))
        self.label_username.setText(_translate("mainWindow", "Inserisci l\'username"))
        self.label_password.setText(_translate("mainWindow", "Inserisci la password"))
        self.pushButton.setText(_translate("mainWindow", "Scrape"))
        self.label_name.setText(_translate("mainWindow", "Inserisci il nome dell\'account"))
        self.label_username_2.setText(_translate("mainWindow", "Informazioni di base:"))
        self.checkBox.setText(_translate("mainWindow", "Post"))
        self.checkBox_2.setText(_translate("mainWindow", "Seguiti"))
        self.checkBox_3.setText(_translate("mainWindow", "Storie in evidenza"))
        self.checkBox_4.setText(_translate("mainWindow", "Storie"))
        self.checkBox_5.setText(_translate("mainWindow", "Post taggati"))
        self.checkBox_6.setText(_translate("mainWindow", "Post salvati"))
        self.checkBox_7.setText(_translate("mainWindow", "Seguaci"))
        self.label_username_3.setText(_translate("mainWindow", "Informazioni aggiuntive:"))
        self.label_username_4.setText(_translate("mainWindow", "- Nome completo"))
        self.label_username_5.setText(_translate("mainWindow", "- Biografia"))
        self.label_username_6.setText(_translate("mainWindow", "- Numero di post"))
        self.label_username_7.setText(_translate("mainWindow", "- Immagine profilo"))
        self.label_username_8.setText(_translate("mainWindow", "- Account verificato (si/no) e tipo di account"))
        self.menuConfiguration.setTitle(_translate("mainWindow", "Configuration"))
        self.menuCase.setTitle(_translate("mainWindow", "Case"))
        self.menuAcquisition.setTitle(_translate("mainWindow", "Acquisition"))

