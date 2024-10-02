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
from view.audio_setting import AudioSetting
from view.util import enable_audio_recording


from controller.configurations.tabs.screenrecorder.screenrecorder import (
    ScreenRecorder as ScreenRecorderConfigurationController,
)

from common.utility import get_platform


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

        # ENABLE AUDIO RECORDING
        self.enable_audio_recording = self.tab.findChild(
            QtWidgets.QCheckBox, "enable_audio_recording"
        )

        self.enable_audio_recording.stateChanged.connect(
            self.__is_enabled_audio_recording
        )

        # AUDIO RECORDING BOX
        self.audio_recording_box = self.tab.findChild(
            QtWidgets.QFrame, "audio_recording_box"
        )

        if get_platform() == "lin" or get_platform() == "other":
            self.audio_recording_box.setVisible(False)

        # SCREEN RECORDER FILENAME
        self.screen_recorder_filename = self.tab.findChild(
            QtWidgets.QLineEdit, "screen_recorder_filename"
        )

        # SETTING AUDIO BUTTON
        self.verify_audio_setting = self.tab.findChild(
            QtWidgets.QPushButton, "verify_audio_setting"
        )
        self.verify_audio_setting.clicked.connect(self.__verify_audio_setting)

        # TEMPORARY LABEL
        self.temporary_msg = self.tab.findChild(QtWidgets.QLabel, "temporary_msg")
        self.temporary_msg.setVisible(False)

    def __verify_audio_setting(self):
        dialog = AudioSetting()
        dialog.accepted.connect(self.__enable_audio_recording)
        dialog.exec()

    def __enable_audio_recording(self):
        if self.enable_screen_recorder.isChecked() and enable_audio_recording():
            self.verify_audio_setting.setEnabled(True)
            self.enable_audio_recording.setEnabled(True)
            app = QtWidgets.QApplication.instance()
            if hasattr(app, "is_enabled_audio_recording"):
                self.enable_audio_recording.setChecked(getattr(app, "is_enabled_audio_recording"))
                self.temporary_msg.setVisible(getattr(app, "is_enabled_audio_recording"))

    def __is_enabled_screen_recorder(self):
        self.screen_recorder_filename.setEnabled(
            self.enable_screen_recorder.isChecked()
        )
        self.verify_audio_setting.setEnabled(self.enable_screen_recorder.isChecked())
        self.__enable_audio_recording()

    def __is_enabled_audio_recording(self):
        app = QtWidgets.QApplication.instance()
        self.temporary_msg.setVisible(self.enable_audio_recording.isChecked())
        setattr(
            app, "is_enabled_audio_recording", self.enable_audio_recording.isChecked()
        )

    def __set_current_config_values(self):
        self.enable_screen_recorder.setChecked(self.__options["enabled"])
        self.screen_recorder_filename.setText(self.__options["filename"])

        self.__is_enabled_screen_recorder()
        self.__enable_audio_recording()

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
