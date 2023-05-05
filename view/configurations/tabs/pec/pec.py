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

from PyQt5 import QtCore, QtWidgets
from controller.configurations.tabs.pec.pec import Pec as PecController
from common.constants.view.pec import pec

__is_tab__ = True


class Pec(QtWidgets.QWidget):

    def __init__(self, parent=None):

        super(Pec, self).__init__(parent)

        self.controller = PecController()
        self.options = self.controller.options

        self.setObjectName("configuration_pec")

        self.initUI()
        self.retranslateUi()
        self.__set_current_config_values()

    def initUI(self):

        # ENABLE CHECKBOX
        self.enabled_checkbox = QtWidgets.QCheckBox(self)
        self.enabled_checkbox.setGeometry(QtCore.QRect(10, 30, 270, 70))
        self.enabled_checkbox.stateChanged.connect(self.__is_enabled_pec)
        self.enabled_checkbox.setObjectName("enabled")


        # CREDENTIAL GROUPBOX
        self.group_box_credential = QtWidgets.QGroupBox(self)
        self.group_box_credential.setGeometry(QtCore.QRect(10, 90, 510, 70))
        self.group_box_credential.setObjectName("group_box_credential")
        self.form_layout_widget_credential = QtWidgets.QWidget(self.group_box_credential)
        self.form_layout_widget_credential.setGeometry(QtCore.QRect(10, 30, 491, 24))
        self.form_layout_widget_credential.setObjectName("form_layout_widget_credential")
        self.horizontal_Layout_credential = QtWidgets.QHBoxLayout(self.form_layout_widget_credential)
        self.horizontal_Layout_credential.setContentsMargins(0, 0, 0, 0)
        self.horizontal_Layout_credential.setObjectName("horizontal_Layout_credential")
        self.label_pec_email = QtWidgets.QLabel(self.form_layout_widget_credential)
        self.label_pec_email.setObjectName("label_pec_email")
        self.horizontal_Layout_credential.addWidget(self.label_pec_email)
        self.pec_email = QtWidgets.QLineEdit(self.form_layout_widget_credential)
        self.pec_email.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pec_email.sizePolicy().hasHeightForWidth())
        self.pec_email.setSizePolicy(sizePolicy)
        self.pec_email.setObjectName("pec_email")
        self.horizontal_Layout_credential.addWidget(self.pec_email)
        self.label_password = QtWidgets.QLabel(self.form_layout_widget_credential)
        self.label_password.setObjectName("label_password")
        self.horizontal_Layout_credential.addWidget(self.label_password)
        self.password = QtWidgets.QLineEdit(self.form_layout_widget_credential)
        self.password.setObjectName("password")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.horizontal_Layout_credential.addWidget(self.password)

        #RETRIES GROUPBOX
        self.group_box_retries = QtWidgets.QGroupBox(self)
        self.group_box_retries.setGeometry(QtCore.QRect(530, 90, 140, 70))
        self.group_box_retries.setObjectName("group_box_retries")
        self.retries = QtWidgets.QSpinBox(self.group_box_retries)
        self.retries.setGeometry(QtCore.QRect(20, 30, 80, 22))
        self.retries.setObjectName("retries")

        #SERVER GROUPBOX
        self.group_box_server = QtWidgets.QGroupBox(self)
        self.group_box_server.setGeometry(QtCore.QRect(10, 170, 660, 90))
        self.group_box_server.setObjectName("group_box_server")

        self.form_layout_widget_IMAP = QtWidgets.QWidget(self.group_box_server)
        self.form_layout_widget_IMAP.setGeometry(QtCore.QRect(10, 20, 511, 24))
        self.form_layout_widget_IMAP.setObjectName("form_layout_widget_server_IMAP")
        self.horizontal_layout_IMAP = QtWidgets.QHBoxLayout(self.form_layout_widget_IMAP)
        self.horizontal_layout_IMAP.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout_IMAP.setObjectName("horizontal_layout_server_IMAP")

        self.label_imap_server = QtWidgets.QLabel(self.form_layout_widget_IMAP)
        self.label_imap_server.setObjectName("label_imap_server")
        self.horizontal_layout_IMAP.addWidget(self.label_imap_server)

        self.imap_server = QtWidgets.QLineEdit(self.form_layout_widget_IMAP)
        self.imap_server.setEnabled(True)
        self.imap_server.setObjectName("imap_server")
        self.horizontal_layout_IMAP.addWidget(self.imap_server)

        self.label_imap_port = QtWidgets.QLabel(self.form_layout_widget_IMAP)
        self.label_imap_port.setObjectName("label_imap_port")
        self.horizontal_layout_IMAP.addWidget(self.label_imap_port)
        self.imap_port = QtWidgets.QLineEdit(self.form_layout_widget_IMAP)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imap_port.sizePolicy().hasHeightForWidth())
        self.imap_port.setSizePolicy(sizePolicy)
        self.imap_port.setObjectName("imap_port")
        self.horizontal_layout_IMAP.addWidget(self.imap_port)


        self.form_layout_widget_SMTP = QtWidgets.QWidget(self.group_box_server)
        self.form_layout_widget_SMTP.setGeometry(QtCore.QRect(10, 50, 511, 24))
        self.form_layout_widget_SMTP.setObjectName("form_layout_widget_SMTP")

        self.horizontal_layout_SMTP = QtWidgets.QHBoxLayout(self.form_layout_widget_SMTP)
        self.horizontal_layout_SMTP.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout_SMTP.setObjectName("horizontal_layout_SMTP")

        self.label_smtp_server = QtWidgets.QLabel(self.form_layout_widget_SMTP)
        self.label_smtp_server.setObjectName("label_smtp_server")

        self.horizontal_layout_SMTP.addWidget(self.label_smtp_server)
        self.smtp_server = QtWidgets.QLineEdit(self.form_layout_widget_SMTP)
        self.smtp_server.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.smtp_server.sizePolicy().hasHeightForWidth())
        self.smtp_server.setSizePolicy(sizePolicy)
        self.smtp_server.setObjectName("smtp_server")
        self.horizontal_layout_SMTP.addWidget(self.smtp_server)

        self.label_smtp_port = QtWidgets.QLabel(self.form_layout_widget_SMTP)
        self.label_smtp_port.setObjectName("label_smtp_port")
        self.horizontal_layout_SMTP.addWidget(self.label_smtp_port)
        self.smtp_port = QtWidgets.QLineEdit(self.form_layout_widget_SMTP)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.smtp_port.sizePolicy().hasHeightForWidth())
        self.smtp_port.setSizePolicy(sizePolicy)
        self.smtp_port.setObjectName("smtp_port")
        self.horizontal_layout_SMTP.addWidget(self.smtp_port)
        

    def retranslateUi(self):
        self.setWindowTitle(pec.WINDOW_TITLE)
        self.enabled_checkbox.setText(pec.ENABLE) 
        self.group_box_credential.setTitle(pec.CREDENTIAL_CONFIGURATION)
        self.label_pec_email.setText(pec.LABEL_EMAIL)
        self.label_password.setText(pec.LABEL_PASSWORD)
        self.group_box_retries.setTitle(pec.RETRIES_NUMBER)
        self.group_box_server.setTitle(pec.SERVER_CONFIGURATION)
        self.label_imap_server.setText(pec.LABEL_IMAP_SERVER)
        self.label_imap_port.setText(pec.LABEL_IMAP_PORT)
        self.label_smtp_server.setText(pec.LABEL_SMPT_SERVER)
        self.label_smtp_port.setText(pec.LABEL_SMPT_PORT)
                                     
    def __is_enabled_pec(self):
        self.group_box_credential.setEnabled(self.enabled_checkbox.isChecked())
        self.group_box_retries.setEnabled(self.enabled_checkbox.isChecked())
        self.group_box_server.setEnabled(self.enabled_checkbox.isChecked())


    def __set_current_config_values(self):
        self.enabled_checkbox.setChecked(self.controller.options['enabled'])
        self.pec_email.setText(self.controller.options['pec_email'])
        self.password.setText(self.controller.options['password'])
        self.smtp_server.setText(self.controller.options['smtp_server'])
        self.smtp_port.setText(self.controller.options['smtp_port'])
        self.imap_server.setText(self.controller.options['imap_server'])
        self.imap_port.setText(self.controller.options['imap_port'])
        self.retries.setValue(self.controller.options['retries'])

        self.__is_enabled_pec()

    def __get_current_values(self):
        for keyword in self.options:
            item = self.findChild(QtCore.QObject, keyword)
            value = ""
            if item is not None:
                if isinstance(item, QtWidgets.QLineEdit):
                    value = item.text()
                elif isinstance(item, QtWidgets.QCheckBox):
                    value = item.isChecked()
                elif isinstance(item, QtWidgets.QSpinBox):
                    value = item.value()

                self.options[keyword] = value

    def accept(self) -> None:
        self.__get_current_values()
        self.controller.options = self.options

    def reject(self) -> None:
        pass