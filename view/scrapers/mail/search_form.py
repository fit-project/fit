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


class MailSearchForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MailSearchForm, self).__init__(parent)
        self.email_validator = QRegularExpressionValidator(
            QRegularExpression("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
        )
        self.is_valid_email = False
        self.emails_to_validate = []

        self.init_ui()

    def init_ui(self):
        font = QFont()
        font.setPointSize(10)

        # SEARCH FORM
        self.search_group_box = QtWidgets.QGroupBox(self.parent())
        self.search_group_box.setGeometry(QRect(50, 260, 430, 240))
        self.search_group_box.setEnabled(False)

        # FROM FIELD
        self.input_from = QtWidgets.QLineEdit(self.search_group_box)
        self.input_from.setGeometry(QRect(130, 30, 240, 20))
        self.input_from.setFont(font)
        self.input_from.textEdited.connect(self.__validate_input)
        self.input_from.setObjectName("input_sender")
        self.input_from.setPlaceholderText(search_pec.PLACEHOLDER_FROM)

        self.input_from.textChanged.connect(self.__on_text_changed)
        self.input_from.editingFinished.connect(self.__on_editing_finished)
        self.emails_to_validate.append(self.input_from.objectName())

        # FROM LABEL
        self.label_from = QtWidgets.QLabel(self.search_group_box)
        self.label_from.setGeometry(QRect(40, 30, 80, 20))
        self.label_from.setFont(font)
        self.label_from.setAlignment(Qt.AlignmentFlag.AlignRight)

        # TO FIELD
        self.input_to = QtWidgets.QLineEdit(self.search_group_box)
        self.input_to.setGeometry(QRect(130, 65, 240, 20))
        self.input_to.setFont(font)
        self.input_to.textEdited.connect(self.__validate_input)
        self.input_to.setObjectName("input_recipient")
        self.input_to.setPlaceholderText(search_pec.PLACEHOLDER_TO)
        self.input_to.editingFinished.connect(self.__on_editing_finished)
        self.input_to.textChanged.connect(self.__on_text_changed)
        self.emails_to_validate.append(self.input_to.objectName())

        # TO LABEL
        self.label_to = QtWidgets.QLabel(self.search_group_box)
        self.label_to.setGeometry(QRect(40, 65, 80, 20))
        self.label_to.setFont(font)
        self.label_to.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_to.setObjectName("label_recipient")

        # SUBJECT FIELD
        self.input_subject = QtWidgets.QLineEdit(self.search_group_box)
        self.input_subject.setGeometry(QRect(130, 100, 240, 20))
        self.input_subject.setFont(font)
        self.input_subject.setPlaceholderText(search_pec.PLACEHOLDER_SUBJECT)

        # SUBJECT LABEL
        self.label_subject = QtWidgets.QLabel(self.search_group_box)
        self.label_subject.setGeometry(QRect(40, 100, 80, 20))
        self.label_subject.setFont(font)
        self.label_subject.setAlignment(Qt.AlignmentFlag.AlignRight)

        # FROM DATE FIELD
        self.input_from_date = QtWidgets.QDateEdit(self.search_group_box)
        self.input_from_date.setGeometry(QRect(130, 135, 240, 20))
        self.input_from_date.setFont(font)
        self.input_from_date.setDate(QDate.currentDate().addDays(-14))
        self.input_from_date.setObjectName("input_from_date")

        # FROM DATE LABEL
        self.label_from_date = QtWidgets.QLabel(self.search_group_box)
        self.label_from_date.setGeometry(QRect(40, 135, 80, 20))
        self.label_from_date.setFont(font)
        self.label_from_date.setAlignment(Qt.AlignmentFlag.AlignRight)

        # TO DATE FIELD
        self.input_to_date = QtWidgets.QDateEdit(self.search_group_box)
        self.input_to_date.setGeometry(QRect(130, 170, 240, 20))
        self.input_to_date.setFont(font)
        self.input_to_date.setDate(QDate.currentDate())

        # TO DATE LABEL
        self.label_to_date = QtWidgets.QLabel(self.search_group_box)
        self.label_to_date.setGeometry(QRect(40, 170, 80, 20))
        self.label_to_date.setFont(font)
        self.label_to_date.setAlignment(Qt.AlignmentFlag.AlignRight)

        # SEARCH BUTTON
        self.search_button = QtWidgets.QPushButton(self.search_group_box)
        self.search_button.setGeometry(QRect(345, 205, 75, 25))
        self.search_button.setFont(font)

        self.retranslateUi()

    def retranslateUi(self):
        self.search_group_box.setTitle(search_pec.CRITERIA)
        self.label_from.setText(search_pec.LABEL_FROM)
        self.label_to.setText(search_pec.LABEL_TO)
        self.label_subject.setText(search_pec.LABEL_SUBJECT)
        self.label_from_date.setText(search_pec.LABEL_FROM_DATE)
        self.label_to_date.setText(search_pec.LABEL_TO_DATE)
        self.search_button.setText(search_pec.SEARCH_BUTTON)

    def enable_search(self, enable):
        self.search_group_box.setEnabled(enable)
        self.search_button.setEnabled(enable)

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

    def __on_editing_finished(self):
        if (
            isinstance(self.sender(), QtWidgets.QLineEdit)
            and self.sender().objectName() in self.emails_to_validate
            and self.sender().text() == ""
            and self.search_button.isEnabled() is False
        ):
            self.is_valid_email = True
            self.sender().setStyleSheet("")
            self.search_button.setEnabled(True)

    def __validate_input(self, text):
        sender = self.sender()
        sender.setText(text.replace(" ", ""))
