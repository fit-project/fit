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

from controller.configurations.tabs.general.typesproceedings import TypesProceedings as TypesProceedingsController

__is_tab__ = False

class TypesProceedings(QtWidgets.QGroupBox):

    def __init__(self, parent=None):

      super(TypesProceedings, self).__init__(parent)

      self.controller = TypesProceedingsController()

      self.setObjectName("general")

      self.initUI()
      self.retranslateUi()
      self.types_proceedings.setPlainText(','.join([str(elem) for elem in self.controller.names]))

    def initUI(self):
        self.setGeometry(QtCore.QRect(10, 250, 691, 131))
        self.setObjectName("group_box_types_proceedings")
        self.types_proceedings = QtWidgets.QPlainTextEdit(self)
        self.types_proceedings.setGeometry(QtCore.QRect(20, 30, 601, 87))
        self.types_proceedings.setObjectName("types_proceedings")
    
    def retranslateUi(self):
      _translate = QtCore.QCoreApplication.translate
      self.setTitle(_translate("ConfigurationView", "Proceedings Type List (comma character is separator)"))

    def accept(self) -> None:
      self.controller.names = self.types_proceedings.toPlainText().split(',')
    
    def reject(self) -> None:
      pass

