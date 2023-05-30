#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

from PyQt6 import QtCore, QtGui, QtWidgets

from controller.configurations.tabs.general.typesproceedings import TypesProceedings as TypesProceedingsController

__is_tab__ = False

class TypesProceedings(QtWidgets.QGroupBox):

    def __init__(self, parent=None):

      super(TypesProceedings, self).__init__(parent)

      self.controller = TypesProceedingsController()

      self.initUI()
      self.retranslateUi()
      self.types_proceedings.setPlainText(','.join([str(elem) for elem in self.controller.names]))

    def initUI(self):
        self.setGeometry(QtCore.QRect(10, 160, 691, 91))
        self.setObjectName("group_box_types_proceedings")
        self.types_proceedings = QtWidgets.QPlainTextEdit(self)
        self.types_proceedings.setGeometry(QtCore.QRect(20, 20, 601, 61))
        self.types_proceedings.setObjectName("types_proceedings")
    
    def retranslateUi(self):
      _translate = QtCore.QCoreApplication.translate
      self.setTitle(_translate("ConfigurationView", "Proceedings Type List (comma character is separator)"))

    def accept(self) -> None:
      self.controller.names = self.types_proceedings.toPlainText().split(',')
    
    def reject(self) -> None:
      pass

