#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


import typing
from PyQt6 import QtGui, QtWidgets


from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView


class MenuBar(QtWidgets.QMenuBar):
    def __init__(self, parent, case_info) -> None:
        super().__init__(parent)

        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()

        self.case_view = CaseView(case_info, self)
        self.case_view.hide()

    def add_default_actions(self):
        # CONFIGURATION ACTION
        configuration_action = QtGui.QAction("Configuration", self)
        configuration_action.setStatusTip("Show configuration info")
        configuration_action.triggered.connect(self.__configuration)
        self.addAction(configuration_action)

        # CASE ACTION
        case_action = QtGui.QAction("Case", self)
        case_action.setStatusTip("Show case info")
        case_action.triggered.connect(self.__case)
        self.addAction(case_action)

    def enable_actions(self, enabled):
        for action in self.actions():
            if action.text() == "Configuration" or action.text() == "Case":
                action.setEnabled(enabled)

    def __configuration(self):
        self.configuration_view.exec()

    def __case(self):
        self.case_view.exec()
