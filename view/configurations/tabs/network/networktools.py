#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


from PyQt6 import QtCore, QtWidgets

from view.configurations.tabs.network.networkcheck import NetworkCheck as NetworkCheckView
from controller.configurations.tabs.network.networktools import NetworkTools as NetworkToolsController
from common.constants.view.network import *


__is_tab__ = True


class NetworkTools(QtWidgets.QWidget):

    def __init__(self, parent=None):

        super(NetworkTools, self).__init__(parent)

        self.controller = NetworkToolsController()
        self.configuration = self.controller.configuration

        self.setObjectName("configuration_option")

        self.initUI()
        self.retranslateUi()
        self.__set_current_config_values()

    def initUI(self):
        #-----
        self.enable_network_tools_box = QtWidgets.QGroupBox(parent=self)
        self.enable_network_tools_box.setGeometry(QtCore.QRect(10, 20, 691, 171))
        self.enable_network_tools_box.setObjectName("enable_network_tools_box")

        self.whois_checkbox = QtWidgets.QCheckBox(parent=self.enable_network_tools_box)
        self.whois_checkbox.setGeometry(QtCore.QRect(20, 20, 251, 17))
        self.whois_checkbox.setObjectName("whois")

        self.headers_checkbox = QtWidgets.QCheckBox(parent=self.enable_network_tools_box)
        self.headers_checkbox.setGeometry(QtCore.QRect(20, 60, 391, 17))
        self.headers_checkbox.setObjectName("headers")

        self.traceroute_checkbox = QtWidgets.QCheckBox(parent=self.enable_network_tools_box)
        self.traceroute_checkbox.setGeometry(QtCore.QRect(20, 80, 91, 17))
        self.traceroute_checkbox.setChecked(True)
        self.traceroute_checkbox.setObjectName("traceroute")

        self.ssl_keylog_checkbox = QtWidgets.QCheckBox(parent=self.enable_network_tools_box)
        self.ssl_keylog_checkbox.setGeometry(QtCore.QRect(20, 100, 111, 17))
        self.ssl_keylog_checkbox.setChecked(True)
        self.ssl_keylog_checkbox.setObjectName("ssl_keylog")

        self.nslookup_checkbox = QtWidgets.QCheckBox(parent=self.enable_network_tools_box)
        self.nslookup_checkbox.setGeometry(QtCore.QRect(20, 40, 331, 17))
        self.nslookup_checkbox.setObjectName("nslookup")

        self.ssl_certificate_checkbox = QtWidgets.QCheckBox(parent=self.enable_network_tools_box)
        self.ssl_certificate_checkbox.setGeometry(QtCore.QRect(20, 120, 121, 17))
        self.ssl_certificate_checkbox.setChecked(True)
        self.ssl_certificate_checkbox.setObjectName("ssl_certificate")


        # PROCEEDINGS TYPE LIST
        self.group_box_network_check = NetworkCheckView(self)

    def retranslateUi(self):
        self.setWindowTitle(NETWORK_OPTIONS_TITLE)
        self.enable_network_tools_box.setTitle(GROUP_BOX_TITLE_NETWORK_TOOLS)
        self.whois_checkbox.setText(WHOIS)
        self.headers_checkbox.setText(HEADERS)
        self.ssl_keylog_checkbox.setText(SSL_KEYLOG)
        self.nslookup_checkbox.setText(NSLOOKUP)
        self.ssl_certificate_checkbox.setText(SSL_CERTIFICATE)
        self.traceroute_checkbox.setText(TRACEROUTE)




    def __set_current_config_values(self):
        self.whois_checkbox.setChecked(self.controller.configuration['whois'])
        self.headers_checkbox.setChecked(self.controller.configuration['headers'])
        self.ssl_keylog_checkbox.setChecked(self.controller.configuration['ssl_keylog'])
        self.nslookup_checkbox.setChecked(self.controller.configuration['nslookup'])
        self.ssl_certificate_checkbox.setChecked(self.controller.configuration['ssl_certificate'])
        self.traceroute_checkbox.setChecked(self.controller.configuration['traceroute'])

    def __get_current_values(self):

        for keyword in self.configuration:
            item = self.findChild(QtCore.QObject, keyword)
            if isinstance(item, QtWidgets.QCheckBox):
              item = item.isChecked()
              self.configuration[keyword] = item

    def accept(self) -> None:
        self.__get_current_values()
        self.controller.configuration = self.configuration
        self.group_box_network_check.accept()

    def reject(self) -> None:
        pass