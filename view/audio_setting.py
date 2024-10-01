#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtGui import QPixmap
from view.clickable_label import ClickableLabel as ClickableLabelView

from common.utility import resolve_path

from common.constants.view.screenrecorder import *

from view.util import (
    is_installed_ffmpeg,
    get_vb_cable_virtual_audio_device,
    is_vb_cable_first_ouput_audio_device,
)


class AudioSetting(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AudioSetting, self).__init__(parent)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        __icon_green = QPixmap(resolve_path("ui/icons/green-mark.png")).scaled(20, 20)
        __icon_red = QPixmap(resolve_path("ui/icons/red-mark.png")).scaled(20, 20)

        self.__init_ui()
        self.ok_button.clicked.connect(self.accept)
        if is_installed_ffmpeg() is True:
            self.ffmpeg_installed_img.setPixmap(__icon_green)
            self.ffmpeg_installed_msg.setText(FFMPEG_INSTALLED)
        else:
            self.ffmpeg_installed_img.setPixmap(__icon_red)
            self.ffmpeg_installed_msg.setText(FFMPEG_NOT_INSTALLED)

        if get_vb_cable_virtual_audio_device() is not None:
            self.vb_cable_installed_img.setPixmap(__icon_green)
            self.vb_cable_installed_msg.setText(VB_CABLE_INSTALLED)
            self.vb_cable_box_first_output_audio_device.setVisible(True)
        else:
            self.vb_cable_installed_img.setPixmap(__icon_red)
            self.vb_cable_installed_msg.setText(VB_CABLE_INSTALLED)
            self.vb_cable_box_first_output_audio_device.setVisible(False)

        if is_vb_cable_first_ouput_audio_device() is True:
            self.vb_cable_first_output_audio_device_img.setPixmap(__icon_green)
            self.vb_cable_first_output_audio_device_msg.setText(
                VB_CABLE_FIRST_OUPUT_AUDIO_DEVICE
            )
        else:
            self.vb_cable_first_output_audio_device_img.setPixmap(__icon_red)
            self.vb_cable_first_output_audio_device_msg.setText(
                VB_CABLE_NOT_FIRST_OUPUT_AUDIO_DEVICE
            )

        self.guide_link.addWidget(
            ClickableLabelView(
                AUDIO_RECORDING_MANAGEMENT_GUIDE_URL, AUDIO_RECORDING_MANAGEMENT_GUIDE
            )
        )

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/audio_setting/audio_setting.ui"), self)
