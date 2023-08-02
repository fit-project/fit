#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os
import string
from PIL import Image

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog

from view.error import Error as ErrorView

from controller.case import Case as CaseController
from controller.configurations.tabs.general.typesproceedings import (
    TypesProceedings as TypesProceedingsController,
)

from common.constants.view.case import *


class CaseForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CaseForm, self).__init__(parent)
        self.controller = CaseController()
        self.cases = self.controller.cases
        self.proceedings = TypesProceedingsController().proceedings
        self.logo_formats = ["JPEG", "PNG"]
        self.logo_minimum_width = 200
        self.logo_background = ["transparent", "white"]

        self.setGeometry(QtCore.QRect(40, 30, 401, 300))
        self.setObjectName("form_layout")

        self.initUI()
        self.retranslateUi()
        self.set_current_cases()
        self.__set_current_config_values()

    def initUI(self):
        self.case_form_layout = QtWidgets.QFormLayout(self)
        self.case_form_layout.setSizeConstraint(
            QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint
        )
        self.case_form_layout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTop
            | QtCore.Qt.AlignmentFlag.AlignTrailing
        )

        self.case_form_layout.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.case_form_layout.setContentsMargins(9, 5, 0, 5)
        self.case_form_layout.setObjectName("case_form_layout")

        font = QtGui.QFont()
        font.setPointSize(10)

        # CASE_NAME_COMBO
        self.name_label = QtWidgets.QLabel(self)
        self.name_label.setFont(font)
        self.name_label.setObjectName("name_label")
        self.case_form_layout.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.name_label
        )
        self.name = QtWidgets.QComboBox(self)
        self.name.editTextChanged.connect(self.__validate_input)
        self.name.setFont(font)
        self.name.setObjectName("name")
        self.case_form_layout.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.name
        )

        # LAWYER_NAME_LINE_EDIT
        self.lawyer_name_label = QtWidgets.QLabel(self)
        self.lawyer_name_label.setFont(font)
        self.lawyer_name_label.setObjectName("lawyer_name_label")
        self.case_form_layout.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.lawyer_name_label
        )
        self.lawyer_name = QtWidgets.QLineEdit(self)
        self.lawyer_name.setFont(font)
        self.lawyer_name.setObjectName("lawyer_name")
        self.case_form_layout.setWidget(
            1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.lawyer_name
        )

        # OPERATOR_LINE_EDIT
        self.operator_label = QtWidgets.QLabel(self)
        self.operator_label.setFont(font)
        self.operator_label.setObjectName("operator_label")
        self.case_form_layout.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.operator_label
        )
        self.operator = QtWidgets.QLineEdit(self)
        self.operator.setFont(font)
        self.operator.setObjectName("operator")
        self.case_form_layout.setWidget(
            2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.operator
        )

        # types_proceedings_COMBO
        self.types_proceedings_label = QtWidgets.QLabel(self)
        self.types_proceedings_label.setFont(font)
        self.types_proceedings_label.setObjectName("proceeding_type_label")
        self.case_form_layout.setWidget(
            3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.types_proceedings_label
        )
        self.types_proceedings = QtWidgets.QComboBox(self)
        self.types_proceedings.setFont(font)
        self.types_proceedings.setObjectName("proceeding_type")
        self.case_form_layout.setWidget(
            3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.types_proceedings
        )

        # COURTHOUSE_LINE_EDIT
        self.courthouse_label = QtWidgets.QLabel(self)
        self.courthouse_label.setFont(font)
        self.courthouse_label.setObjectName("courthouse_label")
        self.case_form_layout.setWidget(
            4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.courthouse_label
        )
        self.courthouse = QtWidgets.QLineEdit(self)
        self.courthouse.setFont(font)
        self.courthouse.setObjectName("courthouse")
        self.case_form_layout.setWidget(
            4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.courthouse
        )

        # proceeding_number_LINE_EDIT
        self.proceeding_number_label = QtWidgets.QLabel(self)
        self.proceeding_number_label.setFont(font)
        self.proceeding_number_label.setObjectName("proceeding_number_label")
        self.case_form_layout.setWidget(
            5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.proceeding_number_label
        )
        self.proceeding_number = QtWidgets.QLineEdit(self)
        self.proceeding_number.setFont(font)
        self.proceeding_number.setObjectName("proceeding_number")
        self.case_form_layout.setWidget(
            5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.proceeding_number
        )

        # LOGO
        logo_label_widget = QtWidgets.QWidget()
        logo_label_layout = QtWidgets.QHBoxLayout(logo_label_widget)
        logo_label_layout.setContentsMargins(0, 0, 0, 0)

        self.logo_icon_info = QtGui.QIcon(
            os.path.join("assets/svg/acquisition", "info-circle.svg")
        )
        self.label_icon_info = QtWidgets.QLabel(self)
        self.label_icon_info.setPixmap(self.logo_icon_info.pixmap(QtCore.QSize(16, 16)))
        self.label_icon_info.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_icon_info.setToolTip(
            LOGO_INFO.format(
                self.logo_minimum_width,
                "/".join(self.logo_formats),
                "/".join(self.logo_background),
            )
        )

        self.logo_label = QtWidgets.QLabel(self)
        self.logo_label.setFont(font)
        self.logo_label.setObjectName("logo_label")
        self.logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        logo_label_layout.addWidget(self.logo_label)
        logo_label_layout.addWidget(self.label_icon_info)

        self.case_form_layout.setWidget(
            6, QtWidgets.QFormLayout.ItemRole.LabelRole, logo_label_widget
        )

        logo_widget = QtWidgets.QWidget()
        logo_layout = QtWidgets.QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)

        self.logo_preview = QtWidgets.QLabel(self)
        self.logo_preview.setObjectName("logo_preview")
        self.logo_preview.setVisible(False)
        logo_layout.addWidget(self.logo_preview)

        self.logo = QtWidgets.QLineEdit(self)
        self.logo.setFont(font)
        self.logo.setObjectName("logo")
        logo_layout.addWidget(self.logo)

        self.tool_button_logo = QtWidgets.QToolButton(self)
        self.tool_button_logo.setFont(font)
        self.tool_button_logo.setObjectName("tool_button_logo")
        self.tool_button_logo.clicked.connect(self.__select_logo)
        logo_layout.addWidget(self.tool_button_logo)
        self.case_form_layout.setWidget(
            6, QtWidgets.QFormLayout.ItemRole.FieldRole, logo_widget
        )

        # NOTES
        self.notes_label = QtWidgets.QLabel(self)
        self.notes_label.setFont(font)
        self.notes_label.setObjectName("notes_label")
        self.case_form_layout.setWidget(
            7, QtWidgets.QFormLayout.ItemRole.LabelRole, self.notes_label
        )
        self.notes = QtWidgets.QTextEdit(self)
        self.notes.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.notes.setFont(font)
        self.notes.setObjectName("notes")
        self.case_form_layout.setWidget(
            7, QtWidgets.QFormLayout.ItemRole.FieldRole, self.notes
        )

        self.retranslateUi()

    def __check_selected_logo(self, file_name):
        err_msg = ""
        img = Image.open(file_name)
        img_format = img.format
        img_width = img.width
        img_main_color = max(img.getcolors(img.size[0] * img.size[1]))
        img = img.convert("RGBA")
        img_alpha_range = img.getextrema()[-1]

        if img_format not in self.logo_formats:
            err_msg = ERR_SELECTED_LOGO_FORMAT.format(
                "/".join(self.logo_formats), img_format
            )
        elif img_width < self.logo_minimum_width:
            err_msg = ERR_SELECTED_LOGO_MINIMUM_WIDTH.format(
                self.logo_minimum_width, img_width
            )
        elif img_main_color[1] != (255, 255, 255) and img_alpha_range == (255, 255):
            err_msg = ERR_SELECTED_LOGO_BG_COLOR.format("/".join(self.logo_background))
        if err_msg != "":
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                CHECK_SELECTED_LOGO,
                err_msg,
                "",
            )

            error_dlg.exec()

        return not bool(err_msg)

    def __select_logo(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Seleziona immagine",
            "",
            "Immagini (*.png *.jpg *.bmp *.gif);;Tutti i file (*)",
        )

        if file_name:
            if self.__check_selected_logo(file_name):
                self.logo.setText(file_name)

                data = ""
                with open(file_name, "rb") as file:
                    data = file.read()
                    self.__set_logo_preview(data)
            else:
                self.__unset_logo_preview()

    def __validate_input(self, text):
        valid_text = self.__remove_chars(text)
        self.name.setEditText(valid_text)

    def __remove_chars(self, text):
        valid_characters = string.ascii_letters + string.digits + "_-"
        valid_text = "".join(c for c in text if c.lower() in valid_characters)
        return valid_text

    def retranslateUi(self):
        self.setWindowTitle(TITLE)
        self.name_label.setText(NAME)
        self.lawyer_name_label.setText(LAWYER)
        self.operator_label.setText(OPERATOR)
        self.types_proceedings_label.setText(PROCEEDING_TYPE)
        self.courthouse_label.setText(COURTHOUSE)
        self.proceeding_number_label.setText(PROCEEDING_NUMBER)
        self.notes_label.setText(NOTES)
        self.logo_label.setText(LOGO)
        self.tool_button_logo.setText(SELECT_EMPTY_LOGO)

    def set_index_from_type_proceedings_id(self, type_proceedings_id):
        self.types_proceedings.setCurrentIndex(
            self.types_proceedings.findData(type_proceedings_id)
        )

    def set_index_from_case_id(self, case_id):
        self.name.setCurrentIndex(self.name.findData(case_id))

    def set_current_cases(self):
        self.name.clear()
        for case in self.cases:
            self.name.addItem(case["name"], case["id"])

    def __set_current_config_values(self):
        for proceedings in self.proceedings:
            self.types_proceedings.addItem(proceedings["name"], proceedings["id"])

    def __set_logo_preview(self, data):
        qp = QtGui.QPixmap()
        qp.loadFromData(data)

        self.logo_height = "auto"
        self.logo_width = "100"

        if qp.height() >= qp.width():
            self.logo_height = "50"
            self.logo_width = "auto"

        qp = qp.scaledToHeight(self.logo.height())
        self.logo_preview.setPixmap(qp)
        self.logo.setVisible(False)
        self.logo_preview.setVisible(True)
        self.tool_button_logo.setText(SELECT_FULL_LOGO)

    def __unset_logo_preview(self):
        self.logo_preview.setPixmap(QtGui.QPixmap())
        self.logo_height = ""
        self.logo_width = ""
        self.tool_button_logo.setText(SELECT_EMPTY_LOGO)
        self.logo.setText("")
        self.logo.setVisible(True)
        self.logo_preview.setVisible(False)

    def set_case_information(self):
        case_info = next(
            (item for item in self.cases if item["name"] == self.name.currentText()),
            None,
        )
        if case_info is not None:
            for keyword, value in case_info.items():
                if keyword == "logo_bin":
                    if value is not None:
                        self.__set_logo_preview(value)
                    else:
                        self.__unset_logo_preview()

                item = self.findChild(QtCore.QObject, keyword)
                if item is not None:
                    if isinstance(item, QtWidgets.QLineEdit) is not False:
                        if value is not None:
                            item.setText(str(value))
                    if isinstance(item, QtWidgets.QTextEdit) is not False:
                        if value is not None:
                            item.setText(str(value))
                    if isinstance(item, QtWidgets.QComboBox):
                        if keyword in "proceeding_type":
                            type_proceeding = next(
                                (
                                    proceeding
                                    for proceeding in self.proceedings
                                    if proceeding["id"] == value
                                ),
                                None,
                            )
                            if type_proceeding is not None:
                                value = type_proceeding["id"]
                            else:
                                value = -1

                            self.set_index_from_type_proceedings_id(value)

    def clear_case_information(self):
        self.lawyer_name.setText("")
        self.operator.setText("")
        self.types_proceedings.setCurrentIndex(-1)
        self.courthouse.setText("")
        self.proceeding_number.setText("")
        self.notes.setText("")
        self.__unset_logo_preview()

    def get_current_case_info(self):
        case_info = next(
            (item for item in self.cases if item["name"] == self.name.currentText()), {}
        )
        for keyword in self.controller.keys:
            item = self.findChild(QtCore.QObject, keyword)
            if item is not None:
                if isinstance(item, QtWidgets.QComboBox):
                    item = item.currentText()
                    if keyword in "proceeding_type":
                        type_proceeding = next(
                            (
                                proceeding
                                for proceeding in self.proceedings
                                if proceeding["name"] == item
                            ),
                            None,
                        )
                        if type_proceeding is not None:
                            item = type_proceeding["id"]
                        else:
                            item = 0

                elif isinstance(item, QtWidgets.QLineEdit) is not False:
                    if item.text():
                        item = item.text()
                    else:
                        item = ""

                elif isinstance(item, QtWidgets.QTextEdit) is not False:
                    if item.toPlainText():
                        item = item.toPlainText()
                    else:
                        item = ""

                case_info[keyword] = item

        case_info["logo_height"] = self.logo_height
        case_info["logo_width"] = self.logo_width

        return case_info
