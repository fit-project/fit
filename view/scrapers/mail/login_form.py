#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import typing
from PyQt6 import QtWidgets
from PyQt6.QtGui import QFont, QRegularExpressionValidator, QIcon, QIntValidator
from PyQt6.QtCore import (
    QRegularExpression,
    QDate,
    Qt,
    QRect,
    QMetaObject,
    QEventLoop,
    QTimer,
)
from view.scrapers.mail.clickable_label import ClickableLabel


from common.constants.view import mail, general
from common.constants.view.pec import search_pec


class MailLoginForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MailLoginForm, self).__init__(parent)
        self.email_validator = QRegularExpressionValidator(
            QRegularExpression("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
        )
        self.is_valid_email = False
        self.emails_to_validate = []

        self.init_ui()

    def init_ui(self):
        font = QFont()
        font.setPointSize(10)

        # CONFIGURATION GROUP BOX
        self.login_group_box = QtWidgets.QGroupBox(self.parent())
        self.login_group_box.setGeometry(QRect(50, 20, 430, 230))

        # EMAIL FIELD
        self.input_email = QtWidgets.QLineEdit(self.login_group_box)
        self.input_email.setGeometry(QRect(130, 30, 240, 20))
        self.input_email.setFont(font)
        self.input_email.textEdited.connect(self.__validate_input)
        self.input_email.setPlaceholderText(search_pec.PLACEHOLDER_USERNAME)
        self.input_email.setObjectName("input_email")
        self.emails_to_validate.append(self.input_email.objectName())

        # EMAIL LABEL
        self.label_email = QtWidgets.QLabel(self.login_group_box)
        self.label_email.setGeometry(QRect(40, 30, 80, 20))
        self.label_email.setFont(font)
        self.label_email.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_email.setObjectName("label_email")

        # PASSWORD FIELD
        self.input_password = QtWidgets.QLineEdit(self.login_group_box)
        self.input_password.setGeometry(QRect(130, 65, 240, 20))
        self.input_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.input_password.setFont(font)
        self.input_password.setPlaceholderText(search_pec.PLACEHOLDER_PASSWORD)
        self.input_password.show()
        self.input_password.setObjectName("input_password")

        # PASSWORD LABEL
        self.label_password = QtWidgets.QLabel(self.login_group_box)
        self.label_password.setGeometry(QRect(40, 65, 80, 20))
        self.label_password.setFont(font)
        self.label_password.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_password.setObjectName("label_password")

        # SERVER FIELD
        self.input_server = QtWidgets.QLineEdit(self.login_group_box)
        self.input_server.setGeometry(QRect(130, 100, 240, 20))
        self.input_server.setFont(font)
        self.input_server.textEdited.connect(self.__validate_input)
        self.input_server.setPlaceholderText(search_pec.PLACEHOLDER_IMAP_SERVER)
        self.input_server.setObjectName("input_server")

        # SERVER LABEL
        self.label_server = QtWidgets.QLabel(self.login_group_box)
        self.label_server.setGeometry(QRect(40, 100, 80, 20))
        self.label_server.setFont(font)
        self.label_server.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_server.setObjectName("label_server")

        # PORT FIELD
        self.input_port = QtWidgets.QLineEdit(self.login_group_box)
        self.input_port.setGeometry(QRect(130, 135, 240, 20))
        self.input_port.setFont(font)
        self.input_port.setPlaceholderText(search_pec.PLACEHOLDER_IMAP_PORT)
        validator = QIntValidator()
        self.input_port.setValidator(validator)
        self.input_port.setObjectName("input_port")

        # PORT LABEL
        self.label_port = QtWidgets.QLabel(self.login_group_box)
        self.label_port.setGeometry(QRect(40, 135, 80, 20))
        self.label_port.setFont(font)
        self.label_port.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_port.setObjectName("label_port")

        # LINK
        self.label_two_factor_auth = ClickableLabel(self.login_group_box)
        self.label_two_factor_auth.setGeometry(QRect(20, 170, 400, 20))
        self.label_two_factor_auth.setObjectName("label_two_factor_auth")

        # LOGIN BUTTON
        self.login_button = QtWidgets.QPushButton(self.login_group_box)
        self.login_button.setGeometry(QRect(345, 195, 75, 25))
        self.login_button.setFont(font)
        self.login_button.setEnabled(False)

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [
            self.input_email,
            self.input_password,
            self.input_server,
            self.input_port,
        ]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        self.retranslateUi()

    def retranslateUi(self):
        self.login_group_box.setTitle(search_pec.SETTINGS)
        self.label_email.setText(search_pec.LABEL_USERNAME)
        self.label_password.setText(search_pec.LABEL_PASSWORD)
        self.label_server.setText(search_pec.LABEL_IMAP_SERVER)
        self.label_port.setText(search_pec.LABEL_IMAP_PORT)
        self.login_button.setText(search_pec.LOGIN_BUTTON)
        self.label_two_factor_auth.setText(mail.TWO_FACTOR_AUTH)

    def enable_login(self, enable):
        self.login_group_box.setEnabled(enable)
        self.login_button.setEnabled(enable)

    def __on_text_changed(self, text):
        if (
            isinstance(self.sender(), QtWidgets.QLineEdit)
            and self.sender().objectName() in self.emails_to_validate
        ):
            state = self.email_validator.validate(text, 0)
            if state[0] != QRegularExpressionValidator.State.Acceptable:
                self.is_valid_email = False
                self.sender().setStyleSheet("border: 1px solid red;")
            else:
                self.is_valid_email = True
                self.sender().setStyleSheet("")

        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.login_button.setEnabled(all_fields_filled and self.is_valid_email)

    def __validate_input(self, text):
        sender = self.sender()
        sender.setText(text.replace(" ", ""))
