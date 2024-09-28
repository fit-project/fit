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
from controller.configurations.tabs.screenrecorder.screenrecorder import ScreenRecorder
from common.constants.view.screenrecorder import *


class AudioRecorderChecker(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AudioRecorderChecker, self).__init__(parent)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__init_ui()
        self.ok_button.clicked.connect(self.__accept)

        self.show_arc_window_at_startup.setChecked(
            ScreenRecorder().options.get("show_arc_window_at_startup")
        )
        self.show_arc_window_at_startup.stateChanged.connect(
            self.__set_show_arc_window_at_startup
        )

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/audio_recoder_checker/arc.ui"), self)

    def __set_show_arc_window_at_startup(self):
        options = ScreenRecorder().options
        options["show_arc_window_at_startup"] = (
            self.show_arc_window_at_startup.isChecked()
        )
        ScreenRecorder().options = options

    def __accept(self):
        self.close()
