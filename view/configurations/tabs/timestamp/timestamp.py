#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtCore, QtWidgets
from view.configurations.tab import Tab

from controller.configurations.tabs.timestamp.timestamp import (
    Timestamp as TimestampController,
)

__is_tab__ = True


class Timestamp(Tab):
    def __init__(self, tab: QtWidgets.QWidget, name: str):
        super().__init__(tab, name)

        self.__options = TimestampController().options

        self.__init_ui()
        self.__set_current_config_values()

    def __init_ui(self):
        # ENABLE TIMESTAMP
        self.enable_timestamp = self.tab.findChild(
            QtWidgets.QCheckBox, "enable_timestamp"
        )

        self.enable_timestamp.stateChanged.connect(self._is_enabled_timestamp)

        # TIMESTAMP SETTINGS BOX
        self.timestamp_settings = self.tab.findChild(
            QtWidgets.QFrame, "timestamp_settings"
        )

        # TIMESTAMP SERVER NAME
        self.timestamp_server_name = self.tab.findChild(
            QtWidgets.QLineEdit, "timestamp_server_name"
        )

        # TIMESTAMP CERTIFICATE URL
        self.timestamp_certificate_url = self.tab.findChild(
            QtWidgets.QLineEdit, "timestamp_certificate_url"
        )

    def _is_enabled_timestamp(self):
        self.timestamp_settings.setEnabled(self.enable_timestamp.isChecked())

    def __set_current_config_values(self):
        self.enable_timestamp.setChecked(self.__options["enabled"])
        self.timestamp_server_name.setText(self.__options["server_name"])
        self.timestamp_certificate_url.setText(self.__options["cert_url"])
        self._is_enabled_timestamp()

    def __get_current_values(self):
        for keyword in self.__options:
            __keyword = keyword

            # REMAPPING KEYWORD
            if keyword == "enabled":
                __keyword = "enable_timestamp"
            elif keyword == "server_name":
                __keyword = "timestamp_server_name"
            elif keyword == "cert_url":
                __keyword = "timestamp_certificate_url"

            item = self.tab.findChild(QtCore.QObject, __keyword)

            if item is not None:
                if isinstance(item, QtWidgets.QLineEdit) is not False and item.text():
                    item = item.text()
                elif isinstance(item, QtWidgets.QCheckBox):
                    item = item.isChecked()

                self.__options[keyword] = item

    def accept(self):
        self.__get_current_values()
        TimestampController().options = self.__options
