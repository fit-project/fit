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
from PyQt6.QtWidgets import QWidget

class MenuBar(QtWidgets.QMenuBar):

    def __init__(self, parent) -> None:
        super().__init__(parent)

    
    def add_default_actions(self):

         # CONFIGURATION ACTION
        configuration_action = QtGui.QAction("Configuration", self)
        configuration_action.setStatusTip("Show configuration info")
        configuration_action.triggered.connect(self.configuration)
        self.addAction(configuration_action)

        # CASE ACTION
        case_action = QtGui.QAction("Case", self)
        case_action.setStatusTip("Show case info")
        case_action.triggered.connect(self.case)
        self.addAction(case_action)