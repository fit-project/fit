#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

from PyQt5 import QtCore, QtGui, QtWidgets

from controller.configurations.tabs.screenrecorder.codec import Codec as CodecController

__is_tab__ = False

class Codec(QtWidgets.QGroupBox):

    def __init__(self, parent=None):

      super(Codec, self).__init__(parent)

      self.controller = CodecController()

      self.setObjectName("general")

      self.initUI()
      self.retranslateUi()
      self.__set_current_config_values()

    def set_index_from_codec_id(self, codec_id):
        self.codec.setCurrentIndex(self.codec.findData(codec_id))

    
    def initUI(self):
        self.setGeometry(QtCore.QRect(210, 90, 160, 70))
        self.setObjectName("group_box_codec")
        self.codec = QtWidgets.QComboBox(self)
        self.codec.setGeometry(QtCore.QRect(20, 30, 80, 22))
        self.codec.setObjectName("codec")
        self.codec.setDisabled(True)
    
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setTitle(_translate("ConfigurationView", "Codec"))

    def __set_current_config_values(self):
        for codec in self.controller.codec:
            self.codec.addItem(codec['name'], codec['id'])
        
        
    