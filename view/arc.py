#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtCore, QtWidgets, uic
from common.utility import resolve_path
from common.constants.view.screenrecorder import *


class ARC(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ARC, self).__init__(parent)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__init_ui()

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/audio_recoder_checker/arc.ui"), self)
