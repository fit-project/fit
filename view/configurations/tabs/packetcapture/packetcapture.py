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
from controller.configurations.tabs.packetcapture.packetcapture import PacketCapture as PacketCaptureController

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
        self.enabled_checkbox.setChecked(self.controller.options['enabled'])
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