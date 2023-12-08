# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QListWidget


from common.constants.view import general, entire_site


class EntireWebsiteForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(EntireWebsiteForm, self).__init__(parent)

        self.init_ui()

    def init_ui(self):
        # set font
        font = QtGui.QFont()
        font.setPointSize(10)

        # URL CONFIGURATION GROUP BOX
        self.url_configuration_group_box = QtWidgets.QGroupBox(self.parent())
        self.url_configuration_group_box.setEnabled(True)
        self.url_configuration_group_box.setFont(font)
        self.url_configuration_group_box.setGeometry(QtCore.QRect(50, 20, 430, 150))
        self.url_configuration_group_box.setObjectName("configuration_group_box")

        self.label_url = QtWidgets.QLabel(self.url_configuration_group_box)
        self.label_url.setGeometry(QtCore.QRect(20, 50, 80, 20))
        self.label_url.setFont(font)
        self.label_url.setObjectName("label_url")

        self.input_url = QtWidgets.QLineEdit(self.url_configuration_group_box)
        self.input_url.setGeometry(QtCore.QRect(50, 50, 350, 20))
        self.input_url.setFont(font)
        self.input_url.textEdited.connect(self.__validate_input)
        self.input_url.setObjectName("input_url")
        self.input_url.setPlaceholderText(entire_site.PLACEHOLDER_URL)

        # LOAD BUTTON
        self.load_website_button = QtWidgets.QPushButton(self.parent())
        self.load_website_button.setGeometry(QtCore.QRect(370, 130, 85, 25))
        self.load_website_button.setObjectName("loadButton")
        self.load_website_button.setFont(font)

        self.load_website_button.setEnabled(False)
        self.input_url.textChanged.connect(
            lambda input: self.__on_text_changed(
                self.input_url, self.load_website_button
            )
        )

        # CUSTOM URL GROUP BOX
        self.custom_urls_group_box = QtWidgets.QGroupBox(self.parent())
        self.custom_urls_group_box.setFont(font)
        self.custom_urls_group_box.setEnabled(False)
        self.custom_urls_group_box.setGeometry(QtCore.QRect(50, 240, 430, 140))
        self.custom_urls_group_box.setObjectName("custom_urls_group_box")

        self.label_custom_url = QtWidgets.QLabel(self.custom_urls_group_box)
        self.label_custom_url.setGeometry(QtCore.QRect(20, 50, 80, 20))
        self.label_custom_url.setFont(font)
        self.label_custom_url.setObjectName("label_custom_url")

        self.input_custom_url = QtWidgets.QLineEdit(self.custom_urls_group_box)
        self.input_custom_url.setGeometry(QtCore.QRect(50, 50, 330, 20))
        self.input_custom_url.setFont(font)
        self.input_custom_url.textEdited.connect(self.__validate_input)
        self.input_custom_url.setObjectName("input_custom_url")
        self.input_custom_url.setPlaceholderText(entire_site.PLACEHOLDER_CUSTOM_URL)

        # ADD BUTTON
        self.add_button = QtWidgets.QPushButton(self.custom_urls_group_box)
        self.add_button.setGeometry(QtCore.QRect(390, 50, 20, 20))
        self.add_button.setStyleSheet(
            "QPushButton { border-radius: 10px; background-color: #4286f4; color: white; font-size: 20px; padding-bottom: 4px; }"
            "QPushButton:hover { background-color: #1c62cc; }"
        )
        self.add_button.setObjectName("add_button")
        self.add_button.setFont(font)
        self.add_button.setEnabled(False)
        self.input_custom_url.textChanged.connect(
            lambda input: self.__on_text_changed(self.input_custom_url, self.add_button)
        )

        # URL PREVIEW GROUP BOX
        self.url_preview_group_box = QtWidgets.QGroupBox(self.parent())
        self.url_preview_group_box.setEnabled(True)
        self.url_preview_group_box.setFont(font)
        self.url_preview_group_box.setGeometry(QtCore.QRect(515, 20, 430, 360))
        self.url_preview_group_box.setObjectName("url_preview_group_box")
        self.list_widget = QListWidget(self.url_preview_group_box)
        layout = QtWidgets.QVBoxLayout(self.url_preview_group_box)
        layout.addWidget(self.list_widget)
        self.url_preview_group_box.setLayout(layout)

        self.retranslateUi()

    def retranslateUi(self):
        self.url_configuration_group_box.setTitle(entire_site.URL_CONFIGURATION)
        self.url_preview_group_box.setTitle(entire_site.CRAWLED_URLS)
        self.label_url.setText(entire_site.URL)
        self.custom_urls_group_box.setTitle(entire_site.CUSTOM_URLS)
        self.load_website_button.setText(general.BUTTON_LOAD_WEBSITE)
        self.label_custom_url.setText(entire_site.URL)
        self.add_button.setText(entire_site.ADD)

    def enable_custom_urls(self, enable):
        self.custom_urls_group_box.setEnabled(enable)

    def __validate_input(self, text):
        sender = self.sender()
        sender.setText(text.replace(" ", ""))

    def __on_text_changed(self, input, button):
        all_field_filled = bool(input.text())
        button.setEnabled(all_field_filled)
