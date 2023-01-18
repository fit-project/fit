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
        self.setGeometry(QtCore.QRect(510, 90, 160, 70))
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
        
        
    