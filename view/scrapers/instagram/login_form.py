# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtCore, QtGui, QtWidgets
from common.constants.view import instagram, general


class InstagramLoginForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(InstagramLoginForm, self).__init__(parent)

        self.init_ui()

    def init_ui(self):
        # set font
        font = QtGui.QFont()
        font.setPointSize(10)

        # LOGIN CONFIGURATION GROUP BOX
        self.login_group_box = QtWidgets.QGroupBox(self.parent())
        self.login_group_box.setEnabled(True)
        self.login_group_box.setFont(font)
        self.login_group_box.setGeometry(QtCore.QRect(50, 40, 430, 140))
        self.login_group_box.setObjectName("configuration_group_box")

        self.input_username = QtWidgets.QLineEdit(self.login_group_box)
        self.input_username.setGeometry(QtCore.QRect(130, 30, 200, 20))
        self.input_username.setFont(font)
        self.input_username.textEdited.connect(self.__validate_input)
        self.input_username.setPlaceholderText(instagram.PLACEHOLDER_USERNAME)
        self.input_username.setObjectName("input_username")

        self.label_username = QtWidgets.QLabel(self.login_group_box)
        self.label_username.setGeometry(QtCore.QRect(40, 30, 80, 20))
        self.label_username.setFont(font)
        self.label_username.setObjectName("label_username")

        self.input_password = QtWidgets.QLineEdit(self.login_group_box)
        self.input_password.setGeometry(QtCore.QRect(130, 60, 200, 20))
        self.input_password.setFont(font)
        self.input_password.setObjectName("input_password")
        self.input_password.setPlaceholderText(instagram.PLACEHOLDER_PASSWORD)
        self.input_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.label_password = QtWidgets.QLabel(self.login_group_box)
        self.label_password.setGeometry(QtCore.QRect(40, 60, 80, 20))
        self.label_password.setFont(font)
        self.label_password.setObjectName("label_password")

        self.input_profile = QtWidgets.QLineEdit(self.login_group_box)
        self.input_profile.setGeometry(QtCore.QRect(130, 90, 200, 20))
        self.input_profile.setFont(font)
        self.input_profile.textEdited.connect(self.__validate_input)
        self.input_profile.setPlaceholderText(instagram.PLACEHOLDER_PROFILE_NAME)
        self.input_profile.setObjectName("input_profile")

        self.label_profile = QtWidgets.QLabel(self.login_group_box)
        self.label_profile.setGeometry(QtCore.QRect(40, 90, 80, 20))
        self.label_profile.setFont(font)
        self.label_profile.setObjectName("label_profile")

        # Verify if input fields are empty
        self.input_fields = [
            self.input_username,
            self.input_password,
            self.input_profile,
        ]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        self.login_button = QtWidgets.QPushButton(self.login_group_box)
        self.login_button.setGeometry(QtCore.QRect(350, 105, 70, 25))
        self.login_button.setObjectName("loginButton")
        self.login_button.setFont(font)
        self.login_button.setEnabled(False)

        self.retranslateUi()

    def retranslateUi(self):
        self.login_group_box.setTitle(instagram.LOGIN_CONFIGURATION)
        self.label_username.setText(instagram.LABEL_USERNAME)
        self.label_password.setText(instagram.LABEL_PASSWORD)
        self.label_profile.setText(instagram.PROFILE_NAME)
        self.login_button.setText(general.BUTTON_LOGIN)

    def enable_login(self, enable):
        self.login_group_box.setEnabled(enable)
        self.login_button.setEnabled(enable)

    def __validate_input(self, text):
        sender = self.sender()
        sender.setText(text.replace(" ", ""))

    def __on_text_changed(self):
        all_field_filled = all(input_field.text() for input_field in self.input_fields)
        self.login_button.setEnabled(all_field_filled)
