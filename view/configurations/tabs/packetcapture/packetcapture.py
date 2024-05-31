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

from controller.configurations.tabs.packetcapture.packetcapture import (
    PacketCapture as PacketCaptureController,
)
from common.utility import is_npcap_installed, get_platform

__is_tab__ = True


class PacketCapture(Tab):
    def __init__(self, tab: QtWidgets.QWidget, name: str):
        super().__init__(tab, name)

        self.__options = PacketCaptureController().options

        self.__init_ui()
        self.__set_current_config_values()

    def __init_ui(self):
        # ENABLE PACKET CAPTURE RECORDER
        self.enable_packet_capture_recorder = self.tab.findChild(
            QtWidgets.QCheckBox, "enable_packet_capture_recorder"
        )

        self.enable_packet_capture_recorder.stateChanged.connect(
            self._is_enabled_packet_capture
        )
        if get_platform() == "win":
            self.enable_packet_capture_recorder.setEnabled(is_npcap_installed())

        # PACKET CAPTURE RECORDER FILENAME
        self.packet_capture_recorder_filename = self.tab.findChild(
            QtWidgets.QLineEdit, "packet_capture_recorder_filename"
        )

    def _is_enabled_packet_capture(self):
        self.packet_capture_recorder_filename.setEnabled(
            self.enable_packet_capture_recorder.isChecked()
        )

    def __set_current_config_values(self):
        enabled = self.__options["enabled"]
        if get_platform() == "win":
            if is_npcap_installed() is False and enabled == True:
                enabled = False

        self.enable_packet_capture_recorder.setChecked(enabled)
        self.packet_capture_recorder_filename.setText(self.__options["filename"])
        self._is_enabled_packet_capture()

    def __get_current_values(self):
        for keyword in self.__options:
            __keyword = keyword

            # REMAPPING KEYWORD
            if keyword == "enabled":
                __keyword = "enable_packet_capture_recorder"
            elif keyword == "filename":
                __keyword = "packet_capture_recorder_filename"

            item = self.tab.findChild(QtCore.QObject, __keyword)

            if item is not None:
                if isinstance(item, QtWidgets.QLineEdit) is not False and item.text():
                    item = item.text()
                elif isinstance(item, QtWidgets.QCheckBox):
                    item = item.isChecked()

                self.__options[keyword] = item

    def accept(self):
        self.__get_current_values()
        PacketCaptureController().options = self.__options
