#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QComboBox

from controller.configurations.tabs.language.language import Language as LanguageController

__is_tab__ = True


class Language(QtWidgets.QWidget):

    def __init__(self, parent=None):

        super(Language, self).__init__(parent)

        self.controller = LanguageController()
        self.options = self.controller.options

        self.setObjectName("configuration_language")

        self.initUI()
        self.retranslateUi()
        self.__set_current_config_values()

    def initUI(self):
        # LANGUAGE
        self.group_box_language = QtWidgets.QGroupBox(self)
        self.group_box_language.setGeometry(QtCore.QRect(10, 90, 661, 91))
        self.group_box_language.setObjectName("group_box_language")

        self.language = QComboBox(self.group_box_language)
        self.language.addItem("Italian")
        self.language.addItem("English")
        self.language.setGeometry(QtCore.QRect(20, 40, 601, 22))
        self.language.setObjectName("language")

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Language", "Language Options"))
        self.group_box_language.setTitle(_translate("Language", "Report Language"))


    def __set_current_config_values(self):
        self.language.setCurrentText(self.controller.options['language'])

    def __get_current_values(self):
        for keyword in self.options:
            item = self.findChild(QtCore.QObject, keyword)

            if item is not None:
                if isinstance(item, QtWidgets.QComboBox) is not False and item.currentText():
                    item = item.currentText()
                elif isinstance(item, QtWidgets.QCheckBox):
                    item = item.isChecked()

                self.options[keyword] = item

    def accept(self) -> None:
        self.__get_current_values()
        self.controller.options = self.options

    def reject(self) -> None:
        pass