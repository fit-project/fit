#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


from PyQt6 import QtWidgets
from view.configurations.tab import Tab


from controller.configurations.tabs.language.language import (
    Language as LanguageController,
)

from common.constants.view.configurations.language import *


import os

__is_tab__ = True


class Language(Tab):

    def __init__(self, tab: QtWidgets.QWidget, name: str):
        super().__init__(tab, name)

        self.__options = LanguageController().options
        self.__init_ui()
        self.__set_current_config_values()

    def __init_ui(self):

        # REPORT LANGUAGE
        self.report_language = self.tab.findChild(
            QtWidgets.QComboBox, "report_language"
        )

        self.report_language.addItem(ITALIAN)
        self.report_language.addItem(ENGLISH)

        self.report_language.lineEdit().setReadOnly(True)
        self.report_language.lineEdit().setPlaceholderText(REPORT_LANGUAGE)

    def __set_current_config_values(self):
        self.report_language.setCurrentText(self.__options["language"])

    def __get_current_values(self):
        self.__options["language"] = self.report_language.currentText()

    def accept(self):
        self.__get_current_values()
        LanguageController().options = self.__options
