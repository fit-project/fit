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


from view.configurations.tab import Tab
from view.clickable_label import ClickableLabel as ClickableLabelView
from view.error import Error as ErrorView

from controller.configurations.tabs.pec.pec import Pec as PecController

from common.utility import resolve_path

from common.constants.view.pec import pec, search_pec
from common.constants import error

__is_tab__ = True


class Pec(Tab):
    def __init__(self, tab: QtWidgets.QWidget, name: str):
        super().__init__(tab, name)

        self.__options = PecController().options

        self.__init_ui()
        self.__set_current_config_values()

    def __init_ui(self):

        # ENABLE PEC LAYOUT
        self.enable_pec_layout = self.tab.findChild(
            QtWidgets.QHBoxLayout, "enable_pec_layout"
        )

        self.enable_pec_layout.addWidget(
            ClickableLabelView(pec.TWO_FACTOR_AUTH_URL, pec.TWO_FACTOR_AUTH)
        )

        # ENABLE PEC
        self.enable_pec = self.tab.findChild(QtWidgets.QCheckBox, "enable_pec")
        self.enable_pec.stateChanged.connect(self.__is_enabled_pec)

        # PEC SETTINGS BOX
        self.pec_settings = self.tab.findChild(QtWidgets.QFrame, "pec_settings")

        # PEC EMAIL
        self.pec_email = self.tab.findChild(QtWidgets.QLineEdit, "pec_email")
        self.pec_email.textEdited.connect(self.__validate_input)

        # PEC PASSWORD
        self.pec_password = self.tab.findChild(QtWidgets.QLineEdit, "pec_password")
        self.pec_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        # RETRIES RETRIES EML DOWNLOAD
        self.retries_eml_download = self.tab.findChild(
            QtWidgets.QLineEdit, "retries_eml_download"
        )
        self.retries_eml_download.setValidator(QIntValidator(0, 10))

        # SERVER IMAP
        self.imap_server = self.tab.findChild(QtWidgets.QLineEdit, "pec_imap_server")
        self.imap_server.textEdited.connect(self.__validate_input)

        # SERVER IMAP PORT
        self.imap_port = self.tab.findChild(QtWidgets.QLineEdit, "pec_imap_server_port")
        self.imap_port.setValidator(QIntValidator(0, 65535))

        # VERIFICATION IMAP BUTTON
        self.verification_imap_button = self.tab.findChild(
            QtWidgets.QPushButton, "verification_imap_button"
        )
        self.verification_imap_button.clicked.connect(self.__verify_imap)

        # VERIFICATION IMAP RESULT ICON
        self.info_imap_img = self.tab.findChild(QtWidgets.QLabel, "info_imap_img")
        self.info_imap_img.setVisible(False)

        # SERVER SMTP
        self.smtp_server = self.tab.findChild(QtWidgets.QLineEdit, "pec_smtp_server")
        self.smtp_server.textEdited.connect(self.__validate_input)

        # SERVER SMTP PORT
        self.smtp_port = self.tab.findChild(QtWidgets.QLineEdit, "pec_smtp_server_port")
        self.smtp_port.setValidator(QIntValidator(0, 65535))

        # VERIFICATION SMTP BUTTON
        self.verification_smtp_button = self.tab.findChild(
            QtWidgets.QPushButton, "verification_smtp_button"
        )
        self.verification_smtp_button.clicked.connect(self.__verify_smtp)

        # VERIFICATION SMTP RESULT ICON
        self.info_smtp_img = self.tab.findChild(QtWidgets.QLabel, "info_smtp_img")
        self.info_smtp_img.setVisible(False)

    def __validate_input(self, text):
        sender = self.tab.sender()
        sender.setText(text.replace(" ", ""))

    def __is_enabled_pec(self):
        self.pec_settings.setEnabled(self.enable_pec.isChecked())

    def __set_current_config_values(self):
        self.enable_pec.setChecked(self.__options["enabled"])
        self.pec_email.setText(self.__options["pec_email"])
        self.pec_password.setText(self.__options["password"])
        self.smtp_server.setText(self.__options["smtp_server"])
        self.smtp_port.setText(self.__options["smtp_port"])
        self.imap_server.setText(self.__options["imap_server"])
        self.imap_port.setText(self.__options["imap_port"])
        self.retries_eml_download.setText(str(self.__options["retries"]))

        self.__is_enabled_pec()

    def __get_current_values(self):
        for keyword in self.__options:
            __keyword = keyword

            # REMAPPING KEYWORD
            if keyword == "enabled":
                __keyword = "enable_pec"
            elif keyword == "password":
                __keyword = "pec_password"
            elif keyword == "retries":
                __keyword = "retries_eml_download"
            elif keyword == "imap_server":
                __keyword = "pec_imap_server"
            elif keyword == "imap_port":
                __keyword = "pec_imap_server_port"
            elif keyword == "smtp_server":
                __keyword = "pec_smtp_server"
            elif keyword == "smtp_port":
                __keyword = "pec_smtp_server_port"

            item = self.tab.findChild(QtCore.QObject, __keyword)

            value = ""
            if item is not None:
                if isinstance(item, QtWidgets.QLineEdit):
                    value = item.text()
                elif isinstance(item, QtWidgets.QCheckBox):
                    value = item.isChecked()
                elif isinstance(item, QtWidgets.QSpinBox):
                    value = item.value()

                self.__options[keyword] = value

    def __verify_imap(self):
        try:
            self.info_imap_img.setVisible(False)
            server = imaplib.IMAP4_SSL(
                self.imap_server.text(), int(self.imap_port.text())
            )
            server.login(self.pec_email.text(), self.pec_password.text())
            server.logout()
            self.info_imap_img.setPixmap(
                QPixmap(resolve_path("ui/icons/green-mark.png")).scaled(20, 20)
            )
            self.info_imap_img.setVisible(True)

        except Exception as e:
            self.info_imap_img.setPixmap(
                QPixmap(resolve_path("ui/icons/red-mark.png")).scaled(20, 20)
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
            server.login(self.pec_email.text(), self.pec_password.text())
            server.quit()
            self.info_smtp_img.setPixmap(
                QPixmap(resolve_path("ui/icons/green-mark.png")).scaled(20, 20)
            )
            self.info_smtp_img.setVisible(True)

        except Exception as e:
            self.info_smtp_img.setPixmap(
                QPixmap(resolve_path("ui/icons/red-mark.png")).scaled(20, 20)
            )
            self.info_smtp_img.setVisible(True)

            error_dlg = ErrorView(
                QMessageBox.Icon.Critical, pec.LOGIN_FAILED, error.LOGIN_ERROR, str(e)
            )
            error_dlg.exec()

    def accept(self) -> None:
        self.__get_current_values()
        PecController().options = self.__options
