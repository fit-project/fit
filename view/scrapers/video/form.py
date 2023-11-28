# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


from PyQt6 import QtCore, QtGui, QtWidgets
from view.scrapers.video.clickable_label import ClickableLabel

from common.constants.view import video, general


class VideoForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(VideoForm, self).__init__(parent)

        self.init_ui()

    def init_ui(self):
        # set font
        font = QtGui.QFont()
        font.setPointSize(10)

        # VIDEO CONFIGURATION GROUP BOX
        self.url_configuration_group_box = QtWidgets.QGroupBox(self.parent())
        self.url_configuration_group_box.setEnabled(True)
        self.url_configuration_group_box.setFont(font)
        self.url_configuration_group_box.setGeometry(QtCore.QRect(50, 20, 430, 200))
        self.url_configuration_group_box.setObjectName("configuration_group_box")

        self.label_url = QtWidgets.QLabel(self.url_configuration_group_box)
        self.label_url.setGeometry(QtCore.QRect(20, 80, 80, 20))
        self.label_url.setFont(font)
        self.label_url.setObjectName("label_url")

        self.input_url = QtWidgets.QLineEdit(self.url_configuration_group_box)
        self.input_url.setGeometry(QtCore.QRect(100, 80, 290, 20))
        self.input_url.setFont(font)
        self.input_url.setObjectName("input_url")
        self.input_url.textEdited.connect(self.__validate_input)
        self.input_url.setPlaceholderText(video.PLACEHOLDER_URL)

        # SUPPORTED SITES
        self.label_supported_sites = ClickableLabel(self.url_configuration_group_box)
        self.label_supported_sites.setGeometry(QtCore.QRect(250, 120, 150, 20))
        self.label_supported_sites.setFont(font)
        self.label_supported_sites.setObjectName("label_supported_sites")

        # AUTH
        """self.label_username = QtWidgets.QLabel(self.url_configuration_group_box)
        self.label_username.setGeometry(QtCore.QRect(20, 120, 80, 20))
        self.label_username.setFont(font)
        self.label_username.setObjectName("label_username")

        self.input_username = QtWidgets.QLineEdit(self.url_configuration_group_box)
        self.input_username.setGeometry(QtCore.QRect(100, 120, 290, 20))
        self.input_username.setFont(font)
        self.input_username.setObjectName("input_username")
        self.input_username.setPlaceholderText(video.PLACEHOLDER_USERNAME)

        self.label_password = QtWidgets.QLabel(self.url_configuration_group_box)
        self.label_password.setGeometry(QtCore.QRect(20, 160, 80, 20))
        self.label_password.setFont(font)
        self.label_password.setObjectName("label_password")

        self.input_password = QtWidgets.QLineEdit(self.url_configuration_group_box)
        self.input_password.setGeometry(QtCore.QRect(100, 160, 290, 20))
        self.input_password.setFont(font)
        self.input_password.setObjectName("input_password")
        self.input_password.setPlaceholderText(video.PLACEHOLDER_PASSWORD)
        self.input_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)"""

        # Verify if input fields are empty
        self.input_fields = [self.input_url]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        # ACQUISITION GROUP BOX
        self.acquisition_group_box = QtWidgets.QGroupBox(self.parent())
        self.acquisition_group_box.setFont(font)
        self.acquisition_group_box.setEnabled(False)
        self.acquisition_group_box.setGeometry(QtCore.QRect(50, 240, 430, 140))
        self.acquisition_group_box.setObjectName("acquisition_group_box")

        # VIDEO QUALITY
        self.label_video_quality = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_video_quality.setGeometry(QtCore.QRect(20, 30, 111, 20))
        self.label_video_quality.setFont(font)
        self.label_video_quality.setObjectName("label_video_quality")

        self.quality = QtWidgets.QComboBox(self.acquisition_group_box)
        self.quality.setGeometry(QtCore.QRect(20, 70, 111, 25))
        self.quality.setFont(font)
        self.quality.setObjectName("quality")

        # ADDITIONAL_INFORMATION
        self.label_additional_information = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_additional_information.setGeometry(QtCore.QRect(180, 30, 150, 20))
        self.label_additional_information.setFont(font)
        self.label_additional_information.setObjectName("label_additional_information")

        self.checkbox_audio = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_audio.setGeometry(QtCore.QRect(180, 50, 100, 17))
        self.checkbox_audio.setFont(font)
        self.checkbox_audio.setObjectName("checkbox_audio")

        self.checkbox_thumbnail = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_thumbnail.setGeometry(QtCore.QRect(180, 70, 100, 17))
        self.checkbox_thumbnail.setFont(font)
        self.checkbox_thumbnail.setObjectName("checkbox_thumbnail")

        self.checkbox_subtitles = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_subtitles.setGeometry(QtCore.QRect(180, 90, 230, 17))
        self.checkbox_subtitles.setFont(font)
        self.checkbox_subtitles.setObjectName("checkbox_subtitles")

        self.checkbox_comments = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_comments.setGeometry(QtCore.QRect(180, 110, 230, 17))
        self.checkbox_comments.setFont(font)
        self.checkbox_comments.setObjectName("checkbox_comments")

        # LOAD BUTTON
        self.load_button = QtWidgets.QPushButton(self.parent())
        self.load_button.setGeometry(QtCore.QRect(400, 385, 80, 25))
        self.load_button.setObjectName("loadButton")
        self.load_button.setFont(font)
        self.load_button.setEnabled(False)

        # VIDEO PREVIEW GROUP BOX
        self.video_preview_group_box = QtWidgets.QGroupBox(self.parent())
        self.video_preview_group_box.setEnabled(True)
        self.video_preview_group_box.setFont(font)
        self.video_preview_group_box.setGeometry(QtCore.QRect(515, 20, 430, 360))
        self.video_preview_group_box.setObjectName("video_preview_group_box")

        self.thumbnail = QtWidgets.QLabel(self.video_preview_group_box)
        self.thumbnail.setGeometry(QtCore.QRect(30, 40, 370, 208))
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setObjectName("thumbnail")

        self.title = QtWidgets.QLabel(self.video_preview_group_box)
        self.title.setGeometry(QtCore.QRect(30, 260, 370, 60))
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.title.setWordWrap(True)

        self.label_duration = QtWidgets.QLabel(self.video_preview_group_box)
        self.label_duration.setGeometry(QtCore.QRect(30, 330, 60, 25))
        self.label_duration.setFont(font)
        self.label_duration.hide()
        self.label_duration.setObjectName("label_duration")

        self.duration = QtWidgets.QLabel(self.video_preview_group_box)
        self.duration.setGeometry(QtCore.QRect(90, 330, 50, 25))
        self.duration.setFont(font)
        self.duration.setObjectName("duration")

        self.retranslateUi()

    def retranslateUi(self):
        self.url_configuration_group_box.setTitle(video.URL_CONFIGURATION)
        self.video_preview_group_box.setTitle(video.PREVIEW)
        self.label_url.setText(video.URL)
        self.label_supported_sites.setText(video.SUPPORTED)
        # self.label_username.setText(video.LABEL_USERNAME)
        # self.label_password.setText(video.LABEL_PASSWORD)
        self.label_duration.setText(video.DURATION)
        self.acquisition_group_box.setTitle(video.ACQUISITON_SETTINGS)
        self.label_video_quality.setText("<strong>" + video.VIDEO_QUALITY + "</strong>")
        self.label_additional_information.setText(
            "<strong>" + video.ADDITIONAL_INFORMATION + "</strong>"
        )
        self.checkbox_audio.setText(video.AUDIO)
        self.checkbox_thumbnail.setText(video.THUMBNAIL)
        self.checkbox_subtitles.setText(video.SUBTITLES)
        self.checkbox_comments.setText(video.COMMENTS)
        self.load_button.setText(general.BUTTON_LOAD)

    def __validate_input(self, text):
        sender = self.sender()
        sender.setText(text.replace(" ", ""))

    def __on_text_changed(self):
        all_field_filled = all(input_field.text() for input_field in self.input_fields)
        self.load_button.setEnabled(all_field_filled)
