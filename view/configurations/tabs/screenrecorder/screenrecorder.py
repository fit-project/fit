#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtCore, QtWidgets
from view.configurations.tab import Tab

from controller.configurations.tabs.screenrecorder.screenrecorder import (
    ScreenRecorder as ScreenRecorderConfigurationController,
)

from view.util import show_screen_recorder_preview_dialog

__is_tab__ = True


class ScreenRecorder(Tab):
    def __init__(self, tab: QtWidgets.QWidget, name: str):
        super().__init__(tab, name)

        self.__options = ScreenRecorderConfigurationController().options

        self.__init_ui()
        self.__set_current_config_values()

    def __init_ui(self):
        # ENABLE SCREEN RECORDER
        self.enable_screen_recorder = self.tab.findChild(
            QtWidgets.QCheckBox, "enable_screen_recorder"
        )

        self.enable_screen_recorder.stateChanged.connect(
            self.__is_enabled_screen_recorder
        )

        # SCREEN RECORDER FILENAME
        self.screen_recorder_filename = self.tab.findChild(
            QtWidgets.QLineEdit, "screen_recorder_filename"
        )

        # SELECT SCREEN OR WINDOW BUTTON
        self.select_screen_window_button = self.tab.findChild(
            QtWidgets.QPushButton, "select_screen_window_button"
        )

        self.select_screen_window_button.clicked.connect(
            show_screen_recorder_preview_dialog
        )

    def __is_enabled_screen_recorder(self):
        self.screen_recorder_filename.setEnabled(
            self.enable_screen_recorder.isChecked()
        )
        self.select_screen_window_button.setEnabled(
            self.enable_screen_recorder.isChecked()
        )

    def __set_current_config_values(self):
        self.enable_screen_recorder.setChecked(self.__options["enabled"])
        self.screen_recorder_filename.setText(self.__options["filename"])

        self.__is_enabled_screen_recorder()

    def __get_current_values(self):
        for keyword in self.__options:

            __keyword = keyword

            # REMAPPING KEYWORD
            if keyword == "enabled":
                __keyword = "enable_screen_recorder"
            elif keyword == "filename":
                __keyword = "screen_recorder_filename"

            item = self.tab.findChild(QtCore.QObject, __keyword)

            if item is not None:
                if (
                    isinstance(item, QtWidgets.QComboBox) is not False
                    and item.currentData()
                ):
                    item = item.currentData()
                elif isinstance(item, QtWidgets.QLineEdit) is not False and item.text():
                    item = item.text()
                elif isinstance(item, QtWidgets.QSpinBox) is not False and item.value():
                    item = item.value()
                elif isinstance(item, QtWidgets.QCheckBox):
                    item = item.isChecked()

                self.__options[keyword] = item

    def accept(self):
        self.__get_current_values()
        ScreenRecorderConfigurationController().options = self.__options
