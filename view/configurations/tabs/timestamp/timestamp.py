#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

from PyQt6 import QtCore, QtWidgets
from controller.configurations.tabs.timestamp.timestamp import Timestamp as TimestampController

__is_tab__ = True


class Timestamp(QtWidgets.QWidget):

    def __init__(self, parent=None):

        super(Timestamp, self).__init__(parent)

        self.controller = TimestampController()
        self.options = self.controller.options

        self.setObjectName("configuration_timestamp")

        self.initUI()
        self.retranslateUi()
        self.__set_current_config_values()

    def initUI(self):
        # ENABLE CHECKBOX
        self.enabled_checkbox = QtWidgets.QCheckBox("Timestamp application", self)
        self.enabled_checkbox.setGeometry(QtCore.QRect(10, 30, 270, 70))
        self.enabled_checkbox.stateChanged.connect(self._is_enabled_timestamp_application)
        self.enabled_checkbox.setObjectName("enabled")

        # SERVER GROUPBOX
        self.group_box_server = QtWidgets.QGroupBox(self)
        self.group_box_server.setGeometry(QtCore.QRect(10, 90, 670, 150))
        self.group_box_server.setObjectName("group_box_server")

        # SERVER NAME GROUPBOX
        self.group_box_server_name = QtWidgets.QGroupBox(self)
        self.group_box_server_name.setGeometry(QtCore.QRect(30, 120, 300, 80))
        self.group_box_server_name.setObjectName("group_box_server_name")
        self.server_name = QtWidgets.QLineEdit(self.group_box_server_name)
        self.server_name.setGeometry(QtCore.QRect(20, 40, 250, 22))
        self.server_name.setObjectName("server_name")

        # CERT URL GROUPBOX
        self.group_box_cert_url = QtWidgets.QGroupBox(self)
        self.group_box_cert_url.setGeometry(QtCore.QRect(350, 120, 300, 80))
        self.group_box_cert_url.setObjectName("group_box_cert_url")
        self.cert_url = QtWidgets.QLineEdit(self.group_box_cert_url)
        self.cert_url.setGeometry(QtCore.QRect(20, 40, 250, 22))
        self.cert_url.setObjectName("cert_url")

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Timestamp", "Timestamp Options"))
        self.group_box_server.setTitle(_translate("Timestamp", "Server"))
        self.group_box_server_name.setTitle(_translate("Timestamp", "Server Name"))
        self.group_box_cert_url.setTitle(_translate("Timestamp", "Certificate Url"))

    def _is_enabled_timestamp_application(self):
        self.group_box_server_name.setEnabled(self.enabled_checkbox.isChecked())
        self.group_box_cert_url.setEnabled(self.enabled_checkbox.isChecked())

    def __set_current_config_values(self):
        self.enabled_checkbox.setChecked(self.controller.options['enabled'])
        self.server_name.setText(self.controller.options['server_name'])
        self.cert_url.setText(self.controller.options['cert_url'])
        self._is_enabled_timestamp_application()

    def __get_current_values(self):
        for keyword in self.options:
            item = self.findChild(QtCore.QObject, keyword)

            if item is not None:
                if isinstance(item, QtWidgets.QLineEdit) is not False and item.text():
                    item = item.text()
                elif isinstance(item, QtWidgets.QCheckBox):
                    item = item.isChecked()

                self.options[keyword] = item

    def accept(self) -> None:
        self.__get_current_values()
        self.controller.options = self.options

    def reject(self) -> None:
        pass