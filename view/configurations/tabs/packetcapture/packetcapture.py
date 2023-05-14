#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

from PyQt5 import QtCore, QtWidgets
from controller.configurations.tabs.packetcapture.packetcapture import PacketCapture as PacketCaptureController
from common.utility import is_npcap_installed, get_platform

__is_tab__ = True

class PacketCapture(QtWidgets.QWidget):

   def __init__(self, parent=None):

      super(PacketCapture, self).__init__(parent)

      self.controller = PacketCaptureController()
      self.options = self.controller.options

      self.setObjectName("configuration_packetcapture")

      self.initUI()
      self.retranslateUi()
      self.__set_current_config_values()

   def initUI(self):
        #ENABLE CHECKBOX
        self.enabled_checkbox = QtWidgets.QCheckBox("Packet Capture Recorder", self)
        self.enabled_checkbox.setGeometry(QtCore.QRect(10, 30, 270, 70))
        self.enabled_checkbox.stateChanged.connect(self._is_enabled_packet_capture)
        if get_platform() == 'win' :
            self.enabled_checkbox.setEnabled(is_npcap_installed())

        self.enabled_checkbox.setObjectName("enabled")


        #FILE NAME
        self.group_box_filename = QtWidgets.QGroupBox(self)
        self.group_box_filename.setGeometry(QtCore.QRect(10, 90, 661, 91))
        self.group_box_filename.setObjectName("group_box_filename")
        self.filename = QtWidgets.QLineEdit(self.group_box_filename)
        self.filename.setGeometry(QtCore.QRect(20, 40, 601, 22))
        self.filename.setObjectName("filename")



   def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("PacketCapture", "Packet Capture Options"))
        self.group_box_filename.setTitle(_translate("PacketCapture", "File Name"))


   def _is_enabled_packet_capture(self):
        self.group_box_filename.setEnabled(self.enabled_checkbox.isChecked())

   def __set_current_config_values(self):
        enabled = self.controller.options['enabled']
        if get_platform() == 'win' :
          if is_npcap_installed() is False and enabled== True:
                    enabled = False

        self.enabled_checkbox.setChecked(enabled)
        self.filename.setText(self.controller.options['filename'])
        self._is_enabled_packet_capture()

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