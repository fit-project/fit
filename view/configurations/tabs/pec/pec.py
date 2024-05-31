#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import imaplib
import smtplib

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QPixmap, QIntValidator
from PyQt6.QtWidgets import QMessageBox, QLabel

from view.clickable_label import ClickableLabel as ClickableLabelView
from view.error import Error as ErrorView

from controller.configurations.tabs.pec.pec import Pec as PecController

from common.utility import resolve_path

from common.constants.view.pec import pec, search_pec
from common.constants import error

__is_tab__ = False


class Pec(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Pec, self).__init__(parent)

        self.controller = PecController()
        self.options = self.controller.options

        self.setObjectName("configuration_pec")

        self.initUI()
        self.retranslateUi()
        self.__set_current_config_values()

    def initUI(self):
        # ENABLE CHECKBOX
        self.enabled_checkbox = QtWidgets.QCheckBox(self)
        self.enabled_checkbox.setGeometry(QtCore.QRect(10, 30, 270, 70))
        self.enabled_checkbox.stateChanged.connect(self.__is_enabled_pec)
        self.enabled_checkbox.setObjectName("enabled")

        self.label_two_factor_auth = ClickableLabelView(pec.TWO_FACTOR_AUTH_URL, self)
        self.label_two_factor_auth.setGeometry(QtCore.QRect(100, 30, 500, 70))
        self.label_two_factor_auth.setObjectName("label_two_factor_auth")

        # CREDENTIAL GROUPBOX
        self.group_box_credential = QtWidgets.QGroupBox(self)
        self.group_box_credential.setGeometry(QtCore.QRect(10, 90, 510, 70))
        self.group_box_credential.setObjectName("group_box_credential")
        self.form_layout_widget_credential = QtWidgets.QWidget(
            self.group_box_credential
        )
        self.form_layout_widget_credential.setGeometry(QtCore.QRect(10, 30, 491, 24))
        self.form_layout_widget_credential.setObjectName(
            "form_layout_widget_credential"
        )
        self.horizontal_Layout_credential = QtWidgets.QHBoxLayout(
            self.form_layout_widget_credential
        )
        self.horizontal_Layout_credential.setContentsMargins(0, 0, 0, 0)
        self.horizontal_Layout_credential.setObjectName("horizontal_Layout_credential")
        self.label_pec_email = QtWidgets.QLabel(self.form_layout_widget_credential)
        self.label_pec_email.setObjectName("label_pec_email")
        self.horizontal_Layout_credential.addWidget(self.label_pec_email)

        self.pec_email = QtWidgets.QLineEdit(self.form_layout_widget_credential)
        self.pec_email.setEnabled(True)
        self.pec_email.textEdited.connect(self.__validate_input)
        self.pec_email.setPlaceholderText(search_pec.PLACEHOLDER_USERNAME)
        self.pec_email.setObjectName("pec_email")
        self.horizontal_Layout_credential.addWidget(self.pec_email)

        self.label_password = QtWidgets.QLabel(self.form_layout_widget_credential)
        self.label_password.setObjectName("label_password")
        self.horizontal_Layout_credential.addWidget(self.label_password)
        self.password = QtWidgets.QLineEdit(self.form_layout_widget_credential)
        self.password.setObjectName("password")
        self.password.setPlaceholderText(search_pec.PLACEHOLDER_PASSWORD)
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.horizontal_Layout_credential.addWidget(self.password)

        # RETRIES GROUPBOX
        self.group_box_retries = QtWidgets.QGroupBox(self)
        self.group_box_retries.setGeometry(QtCore.QRect(530, 90, 140, 70))
        self.group_box_retries.setObjectName("group_box_retries")
        self.retries = QtWidgets.QSpinBox(self.group_box_retries)
        self.retries.setGeometry(QtCore.QRect(20, 30, 80, 22))
        self.retries.setObjectName("retries")

        # SERVER GROUPBOX
        self.group_box_server = QtWidgets.QGroupBox(self)
        self.group_box_server.setGeometry(QtCore.QRect(10, 170, 660, 90))
        self.group_box_server.setObjectName("group_box_server")

        self.form_layout_widget_IMAP = QtWidgets.QWidget(self.group_box_server)
        self.form_layout_widget_IMAP.setGeometry(QtCore.QRect(10, 20, 600, 24))
        self.form_layout_widget_IMAP.setObjectName("form_layout_widget_server_IMAP")
        self.horizontal_layout_IMAP = QtWidgets.QHBoxLayout(
            self.form_layout_widget_IMAP
        )
        self.horizontal_layout_IMAP.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout_IMAP.setObjectName("horizontal_layout_server_IMAP")

        self.label_imap_server = QtWidgets.QLabel(self.form_layout_widget_IMAP)
        self.label_imap_server.setObjectName("label_imap_server")
        self.horizontal_layout_IMAP.addWidget(self.label_imap_server)

        self.imap_server = QtWidgets.QLineEdit(self.form_layout_widget_IMAP)
        self.imap_server.setEnabled(True)
        self.imap_server.textEdited.connect(self.__validate_input)
        self.imap_server.setPlaceholderText(search_pec.PLACEHOLDER_IMAP_SERVER)
        self.imap_server.setObjectName("imap_server")
        self.horizontal_layout_IMAP.addWidget(self.imap_server)

        self.label_imap_port = QtWidgets.QLabel(self.form_layout_widget_IMAP)
        self.label_imap_port.setObjectName("label_imap_port")
        self.horizontal_layout_IMAP.addWidget(self.label_imap_port)
        self.imap_port = QtWidgets.QLineEdit(self.form_layout_widget_IMAP)
        self.imap_port.setPlaceholderText(search_pec.PLACEHOLDER_IMAP_PORT)
        self.imap_port.setObjectName("imap_port")
        validator = QIntValidator()
        self.imap_port.setValidator(validator)
        self.horizontal_layout_IMAP.addWidget(self.imap_port)

        self.verification_imap_button = QtWidgets.QPushButton(
            self.form_layout_widget_IMAP
        )
        self.verification_imap_button.clicked.connect(self.__verify_imap)
        self.verification_imap_button.setObjectName("verification_imap_button")
        self.verification_imap_button.setEnabled(True)
        self.horizontal_layout_IMAP.addWidget(self.verification_imap_button)

        self.info_imap_img = QLabel(self)
        self.info_imap_img.setEnabled(True)
        self.info_imap_img.setPixmap(
            QPixmap(resolve_path("assets/images/red-mark.png")).scaled(20, 20)
        )
        self.info_imap_img.setScaledContents(True)
        self.info_imap_img.setGeometry(QtCore.QRect(630, 192, 20, 20))
        self.info_imap_img.setVisible(False)

        self.form_layout_widget_SMTP = QtWidgets.QWidget(self.group_box_server)
        self.form_layout_widget_SMTP.setGeometry(QtCore.QRect(10, 50, 600, 24))
        self.form_layout_widget_SMTP.setObjectName("form_layout_widget_SMTP")

        self.horizontal_layout_SMTP = QtWidgets.QHBoxLayout(
            self.form_layout_widget_SMTP
        )
        self.horizontal_layout_SMTP.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout_SMTP.setObjectName("horizontal_layout_SMTP")

        self.label_smtp_server = QtWidgets.QLabel(self.form_layout_widget_SMTP)
        self.label_smtp_server.setObjectName("label_smtp_server")

        self.horizontal_layout_SMTP.addWidget(self.label_smtp_server)
        self.smtp_server = QtWidgets.QLineEdit(self.form_layout_widget_SMTP)
        self.smtp_server.setEnabled(True)
        self.smtp_server.textEdited.connect(self.__validate_input)
        self.smtp_server.setPlaceholderText(search_pec.PLACEHOLDER_SMPT_SERVER)
        self.smtp_server.setObjectName("smtp_server")
        self.horizontal_layout_SMTP.addWidget(self.smtp_server)

        self.label_smtp_port = QtWidgets.QLabel(self.form_layout_widget_SMTP)
        self.label_smtp_port.setObjectName("label_smtp_port")
        self.horizontal_layout_SMTP.addWidget(self.label_smtp_port)
        self.smtp_port = QtWidgets.QLineEdit(self.form_layout_widget_SMTP)
        self.smtp_port.setPlaceholderText(search_pec.PLACEHOLDER_SMPT_PORT)
        self.smtp_port.setObjectName("smtp_port")
        self.smtp_port.setValidator(validator)
        self.horizontal_layout_SMTP.addWidget(self.smtp_port)

        self.verification_smtp_button = QtWidgets.QPushButton(
            self.form_layout_widget_SMTP
        )
        self.verification_smtp_button.clicked.connect(self.__verify_smtp)
        self.verification_smtp_button.setObjectName("verification_smtp_button")
        self.verification_smtp_button.setEnabled(True)
        self.horizontal_layout_SMTP.addWidget(self.verification_smtp_button)

        self.info_smtp_img = QLabel(self)
        self.info_smtp_img.setEnabled(True)
        self.info_smtp_img.setPixmap(
            QPixmap(resolve_path("assets/images/red-mark.png")).scaled(20, 20)
        )
        self.info_smtp_img.setScaledContents(True)
        self.info_smtp_img.setGeometry(QtCore.QRect(630, 222, 20, 20))
        self.info_smtp_img.setVisible(False)

    def retranslateUi(self):
        self.setWindowTitle(pec.WINDOW_TITLE)
        self.enabled_checkbox.setText(pec.ENABLE)
        self.group_box_credential.setTitle(pec.CREDENTIAL_CONFIGURATION)
        self.label_pec_email.setText(pec.LABEL_EMAIL)
        self.label_password.setText(pec.LABEL_PASSWORD)
        self.group_box_retries.setTitle(pec.RETRIES_NUMBER)
        self.group_box_server.setTitle(pec.SERVER_CONFIGURATION)
        self.label_imap_server.setText(pec.LABEL_IMAP_SERVER)
        self.label_imap_port.setText(pec.LABEL_IMAP_PORT)
        self.label_smtp_server.setText(pec.LABEL_SMPT_SERVER)
        self.label_smtp_port.setText(pec.LABEL_SMPT_PORT)
        self.verification_imap_button.setText(pec.VERIFY_IMAP)
        self.verification_smtp_button.setText(pec.VERIFY_SMTP)
        self.label_two_factor_auth.setText(pec.TWO_FACTOR_AUTH)

    def __validate_input(self, text):
        sender = self.sender()
        sender.setText(text.replace(" ", ""))

    def __is_enabled_pec(self):
        self.group_box_credential.setEnabled(self.enabled_checkbox.isChecked())
        self.group_box_retries.setEnabled(self.enabled_checkbox.isChecked())
        self.group_box_server.setEnabled(self.enabled_checkbox.isChecked())

    def __set_current_config_values(self):
        self.enabled_checkbox.setChecked(self.controller.options["enabled"])
        self.pec_email.setText(self.controller.options["pec_email"])
        self.password.setText(self.controller.options["password"])
        self.smtp_server.setText(self.controller.options["smtp_server"])
        self.smtp_port.setText(self.controller.options["smtp_port"])
        self.imap_server.setText(self.controller.options["imap_server"])
        self.imap_port.setText(self.controller.options["imap_port"])
        self.retries.setValue(self.controller.options["retries"])

        self.__is_enabled_pec()

    def __get_current_values(self):
        for keyword in self.options:
            item = self.findChild(QtCore.QObject, keyword)
            value = ""
            if item is not None:
                if isinstance(item, QtWidgets.QLineEdit):
                    value = item.text()
                elif isinstance(item, QtWidgets.QCheckBox):
                    value = item.isChecked()
                elif isinstance(item, QtWidgets.QSpinBox):
                    value = item.value()

                self.options[keyword] = value

    def __verify_imap(self):
        try:
            self.info_imap_img.setVisible(False)
            server = imaplib.IMAP4_SSL(
                self.imap_server.text(), int(self.imap_port.text())
            )
            server.login(self.pec_email.text(), self.password.text())
            server.logout()
            self.info_imap_img.setPixmap(
                QPixmap(resolve_path("assets/images/green-mark.png")).scaled(20, 20)
            )
            self.info_imap_img.setVisible(True)

        except Exception as e:
            self.info_imap_img.setPixmap(
                QPixmap(resolve_path("assets/images/red-mark.png")).scaled(20, 20)
            )
            self.info_imap_img.setVisible(True)
            error_dlg = ErrorView(
                QMessageBox.Icon.Critical, pec.LOGIN_FAILED, error.LOGIN_ERROR, str(e)
            )
            error_dlg.exec()

    def __verify_smtp(self):
        try:
            self.info_smtp_img.setVisible(False)
            server = smtplib.SMTP_SSL(
                self.smtp_server.text(), int(self.smtp_port.text())
            )
            server.login(self.pec_email.text(), self.password.text())
            server.quit()
            self.info_smtp_img.setPixmap(
                QPixmap(resolve_path("assets/images/green-mark.png")).scaled(20, 20)
            )
            self.info_smtp_img.setVisible(True)

        except Exception as e:
            self.info_smtp_img.setPixmap(
                QPixmap(resolve_path("assets/images/red-mark.png")).scaled(20, 20)
            )
            self.info_smtp_img.setVisible(True)

            error_dlg = ErrorView(
                QMessageBox.Icon.Critical, pec.LOGIN_FAILED, error.LOGIN_ERROR, str(e)
            )
            error_dlg.exec()

    def accept(self) -> None:
        self.__get_current_values()
        self.controller.options = self.options

    def reject(self) -> None:
        pass
