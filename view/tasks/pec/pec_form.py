# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import imaplib
import os
import time

from PyQt6 import QtCore, QtGui, QtWidgets

from common.utility import resolve_path
from common.constants.view.pec import pec
from common.constants.status import FAIL


class PecForm(QtWidgets.QDialog):
    def __init__(self, parent: None):
        super().__init__()
        self.parent = parent
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )
        self.__setupUi()

    def __setupUi(self):
        self.setObjectName("PECForm")
        self.resize(452, 400)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setWindowIcon(
            QtGui.QIcon(os.path.join(resolve_path("assets/svg/"), "FIT.svg"))
        )

        # PEC USER AND PASSWORD
        self.label_pec_email = QtWidgets.QLabel(self.centralwidget)
        self.label_pec_email.setGeometry(QtCore.QRect(30, 30, 100, 20))
        self.label_pec_email.setObjectName("label_pec_email")
        self.input_pec_email = QtWidgets.QLineEdit(self.centralwidget)
        self.input_pec_email.setGeometry(QtCore.QRect(170, 30, 240, 20))
        self.input_pec_email.setObjectName("input_pec_email")
        pec_regex = QtCore.QRegularExpression(
            "[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"
        )  # check
        validator = QtGui.QRegularExpressionValidator(pec_regex)
        self.input_pec_email.setValidator(validator)
        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QtCore.QRect(30, 60, 100, 20))
        self.label_password.setObjectName("label_password")
        self.input_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QtCore.QRect(170, 60, 240, 20))
        self.input_password.setObjectName("input_password")
        self.input_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        # PEC SMTP INFO
        self.label_smpt_server = QtWidgets.QLabel(self.centralwidget)
        self.label_smpt_server.setGeometry(QtCore.QRect(30, 120, 100, 20))
        self.label_smpt_server.setObjectName("label_smpt_server")
        self.input_smtp_server = QtWidgets.QLineEdit(self.centralwidget)
        self.input_smtp_server.setGeometry(QtCore.QRect(170, 120, 240, 20))
        self.input_smtp_server.setObjectName("input_smtp_server")
        self.label_smpt_port = QtWidgets.QLabel(self.centralwidget)
        self.label_smpt_port.setGeometry(QtCore.QRect(30, 150, 100, 20))
        self.label_smpt_port.setObjectName("label_smpt_port")
        self.input_smtp_port = QtWidgets.QLineEdit(self.centralwidget)
        self.input_smtp_port.setGeometry(QtCore.QRect(170, 150, 50, 20))
        self.input_smtp_port.setObjectName("input_smtp_port")
        validator = QtGui.QIntValidator()
        self.input_smtp_port.setValidator(validator)

        # PEC IMAP INFO
        self.label_imap_server = QtWidgets.QLabel(self.centralwidget)
        self.label_imap_server.setGeometry(QtCore.QRect(30, 190, 100, 20))
        self.label_imap_server.setObjectName("label_imap_server")
        self.input_imap_server = QtWidgets.QLineEdit(self.centralwidget)
        self.input_imap_server.setGeometry(QtCore.QRect(170, 190, 240, 20))
        self.input_imap_server.setObjectName("input_imap_server")
        self.label_imap_port = QtWidgets.QLabel(self.centralwidget)
        self.label_imap_port.setGeometry(QtCore.QRect(30, 220, 100, 20))
        self.label_imap_port.setObjectName("label_imap_port")
        self.input_imap_port = QtWidgets.QLineEdit(self.centralwidget)
        self.input_imap_port.setGeometry(QtCore.QRect(170, 220, 50, 20))
        self.input_imap_port.setObjectName("input_imap_port")
        self.input_imap_port.setValidator(validator)

        # Verify if input fields are empty
        self.input_fields = [
            self.input_pec_email,
            self.input_password,
            self.input_smtp_server,
            self.input_smtp_port,
            self.input_imap_server,
            self.input_imap_port,
        ]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        self.send_button = QtWidgets.QPushButton(self.centralwidget)
        self.send_button.setGeometry(QtCore.QRect(340, 297, 75, 25))
        self.send_button.setObjectName("scrapeButton")
        self.send_button.clicked.connect(self.send)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.send_button.setFont(font)
        self.send_button.setEnabled(False)

        self.skip_button = QtWidgets.QPushButton(self.centralwidget)
        self.skip_button.setGeometry(QtCore.QRect(245, 297, 75, 25))
        self.skip_button.setObjectName("skip_button")
        font.setBold(False)
        self.skip_button.setFont(font)
        self.skip_button.clicked.connect(self.parent.reject)
        self.skip_button.setEnabled(True)

        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(320, 347, 131, 23))
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setValue(0)

        self.output_message = QtWidgets.QLabel(self.centralwidget)
        self.output_message.setGeometry(QtCore.QRect(30, 347, 270, 20))
        self.output_message.setObjectName("outputMessage")

        self.check_box_save_pec_configuration = QtWidgets.QCheckBox(self.centralwidget)
        self.check_box_save_pec_configuration.setGeometry(
            QtCore.QRect(170, 257, 111, 17)
        )
        self.check_box_save_pec_configuration.setObjectName("checkBox")

        if self.parent.options:
            self.input_pec_email.setText(self.parent.options.get("pec_email"))
            self.input_password.setText(self.parent.options.get("password"))
            self.input_smtp_server.setText(self.parent.options.get("smtp_server"))
            self.input_smtp_port.setText(self.parent.options.get("smtp_port"))
            self.input_imap_server.setText(self.parent.options.get("imap_server"))
            self.input_imap_port.setText(self.parent.options.get("imap_port"))

        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(pec.WINDOW_TITLE)
        self.label_pec_email.setText(pec.LABEL_EMAIL + "*")
        self.label_password.setText(pec.LABEL_PASSWORD + "*")
        self.label_smpt_server.setText(pec.LABEL_SMPT_SERVER + "*")
        self.label_smpt_port.setText(pec.LABEL_SMPT_PORT + "*")
        self.label_imap_server.setText(pec.LABEL_IMAP_SERVER + "*")
        self.label_imap_port.setText(pec.LABEL_IMAP_PORT + "*")
        self.send_button.setText(pec.SEND_BUTTON)
        self.skip_button.setText(pec.SKIP_BUTTON)
        self.check_box_save_pec_configuration.setText(
            pec.CHECK_BOX_SAVE_PEC_CONFIGURATION
        )

    def __on_text_changed(self):
        all_field_filled = all(input_field.text() for input_field in self.input_fields)
        self.send_button.setEnabled(all_field_filled)

        effect = QtWidgets.QGraphicsOpacityEffect()
        if all_field_filled:
            effect.setOpacity(0.5)
            self.skip_button.setGraphicsEffect(effect)
        else:
            effect.setOpacity(1)
            self.skip_button.setGraphicsEffect(effect)

    def send(self):
        self.centralwidget.setEnabled(False)
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(500, loop.quit)
        loop.exec()
        if self.parent.options:
            self.parent.options.update(
                {
                    "pec_email": self.input_pec_email.text(),
                    "password": self.input_password.text(),
                    "smtp_server": self.input_smtp_server.text(),
                    "smtp_port": self.input_smtp_port.text(),
                    "imap_server": self.input_imap_server.text(),
                    "imap_port": self.input_imap_port.text(),
                }
            )

        self.output_message.setText(pec.SEND_MESSAGE)
        self.parent.send()
