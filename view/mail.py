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
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QFont, QDoubleValidator, QRegExpValidator
from PyQt5.QtWidgets import QApplication

from controller.mail import Mail as MailController

from view.case import Case as CaseView
from view.mail_scraping import MailScraping as MailScrapingView
from view.error import Error as ErrorView

from common.error import ErrorMessage


class Mail(QtWidgets.QMainWindow):
    stop_signal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Mail, self).__init__(*args, **kwargs)
        self.mail_controller = None
        self.input_email = None
        self.input_password = None
        self.input_server = None
        self.input_port = None
        self.error_msg = ErrorMessage()

    def init(self, case_info):
        self.width = 520
        self.height = 300
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info


        self.setObjectName("email_scrape_window")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("QWidget {background-color: rgb(255, 255, 255);}")



        # IMAP GROUP
        self.imap_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.imap_group_box.setEnabled(True)
        self.imap_group_box.setGeometry(QtCore.QRect(50, 20, 430, 240))
        self.imap_group_box.setObjectName("imap_group_box")

        # EMAIL FIELD
        self.input_email = QtWidgets.QLineEdit(self.centralwidget)
        self.input_email.setGeometry(QtCore.QRect(180, 60, 240, 20))
        self.input_email.setFont(QFont('Arial', 10))
        email_regex = QRegExp("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")  # check
        validator = QRegExpValidator(email_regex)
        self.input_email.setValidator(validator)
        self.input_email.setObjectName("input_email")

        # PASSWORD FIELD
        self.input_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QtCore.QRect(180, 95, 240, 20))
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_password.setFont(QFont('Arial', 10))
        self.input_password.show()
        self.input_password.setObjectName("input_password")

        # SERVER FIELD
        self.input_server = QtWidgets.QLineEdit(self.centralwidget)
        self.input_server.setGeometry(QtCore.QRect(180, 130, 240, 20))
        self.input_server.setFont(QFont('Arial', 10))
        self.input_server.setObjectName("input_server")

        # PORT FIELD
        self.input_port = QtWidgets.QLineEdit(self.centralwidget)
        self.input_port.setGeometry(QtCore.QRect(180, 165, 240, 20))
        self.input_port.setFont(QFont('Arial', 10))
        validator = QDoubleValidator()
        self.input_port.setValidator(validator)
        self.input_port.setObjectName("input_port")

        # DISABLE LOGIN BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_email, self.input_password, self.input_server, self.input_port]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.onTextChanged)

        # set font
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily('Arial')

        # EMAIL LABEL
        self.label_email = QtWidgets.QLabel(self.centralwidget)
        self.label_email.setGeometry(QtCore.QRect(90, 60, 80, 20))
        self.label_email.setFont(font)
        self.label_email.setAlignment(QtCore.Qt.AlignRight)
        self.label_email.setObjectName("label_email")

        # PASSWORD LABEL
        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QtCore.QRect(90, 95, 80, 20))
        self.label_password.setFont(font)
        self.label_password.setAlignment(QtCore.Qt.AlignRight)
        self.label_password.setObjectName("label_password")

        # SERVER LABEL
        self.label_server = QtWidgets.QLabel(self.centralwidget)
        self.label_server.setGeometry(QtCore.QRect(90, 130, 80, 20))
        self.label_server.setFont(font)
        self.label_server.setAlignment(QtCore.Qt.AlignRight)
        self.label_server.setObjectName("label_server")

        # PORT LABEL
        self.label_port = QtWidgets.QLabel(self.centralwidget)
        self.label_port.setGeometry(QtCore.QRect(90, 165, 80, 20))
        self.label_port.setFont(font)
        self.label_port.setAlignment(QtCore.Qt.AlignRight)
        self.label_port.setObjectName("label_port")

        # LOGIN BUTTON
        self.login_button = QtWidgets.QPushButton(self.centralwidget)
        self.login_button.setGeometry(QtCore.QRect(345, 210, 75, 25))
        self.login_button.clicked.connect(self.login)
        self.login_button.setFont(font)
        self.login_button.setObjectName("StartLoginAction")
        self.login_button.setEnabled(False)

        # MENU BAR
        self.setCentralWidget(self.centralwidget)
        self.menuBar().setNativeMenuBar(False)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("email_scrape_window", "Freezing Internet Tool"))
        self.imap_group_box.setTitle(
            _translate("email_scrape_window", "Impostazioni server IMAP"))
        self.label_email.setText(_translate("email_scrape_window", "E-mail*"))
        self.label_password.setText(_translate("email_scrape_window", "Password*"))
        self.label_server.setText(_translate("email_scrape_window", "Server IMAP*"))
        self.label_port.setText(_translate("email_scrape_window", "Port*"))
        self.login_button.setText(_translate("email_scrape_window", "Login"))

    def login(self):

        email = self.input_email.text()
        password = self.input_password.text()
        server = self.input_server.text()
        port = self.input_port.text()
        self.mail_controller = MailController()

        try:
            self.mail_controller.check_server(server, port)
        except Exception as e:  # WRONG SERVER
            error_dlg = ErrorView(QtWidgets.QMessageBox.Information,
                                  self.error_msg.TITLES['server_error'],
                                  self.error_msg.MESSAGES['server_error'],
                                  "Please retry.")
            error_dlg.exec_()
            return

        try:
            self.mail_controller.check_login(email, password)
        except Exception as e:  # WRONG CREDENTIALS
            error_dlg = ErrorView(QtWidgets.QMessageBox.Information,
                                  self.error_msg.TITLES['login_error'],
                                  self.error_msg.MESSAGES['login_error'],
                                  "Please retry.")
            error_dlg.exec_()
            return
        finally:

            mail_scraping = MailScrapingView()
            mail_scraping.hide()
            mail_scraping.init(self.case_info, self.mail_controller)
            mail_scraping.show()

    def onTextChanged(self):
        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.login_button.setEnabled(all_fields_filled)
