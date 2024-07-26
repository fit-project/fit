#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

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


class CaseFormManager:
    def __init__(self, form, temporary=False):
        self.controller = CaseController()
        self.cases = self.controller.cases
        self.proceedings = TypesProceedingsController().proceedings
        self.logo_formats = ["JPEG", "PNG"]
        self.logo_minimum_width = 200
        self.logo_background = ["transparent", "white"]
        self.logo_height = ""
        self.logo_width = ""
        self.__temporary = temporary

        self.form = form
        if self.__temporary is True:
            self.name = self.form.findChild(QtWidgets.QLineEdit, "temporary_name")
        else:
            self.name = self.form.findChild(QtWidgets.QComboBox, "name")

        self.proceeding_type = self.form.findChild(
            QtWidgets.QComboBox, "proceeding_type"
        )

        self.logo_preview = None

        self.__set_logo_info()
        self.__set_current_proceeding_type()
        self.set_current_cases()

        if self.__temporary is False:
            self.name.currentTextChanged.connect(self.__validate_input)

    def __set_logo_info(self):
        logo_container = self.form.findChild(QtWidgets.QFrame, "logo_container")

        for item in logo_container.children():
            if isinstance(item, QtWidgets.QLineEdit):
                self.logo_path = item
            elif isinstance(item, QtWidgets.QPushButton):
                self.logo_button = item
                self.logo_button.clicked.connect(self.__select_logo)
            elif isinstance(item, QtWidgets.QHBoxLayout):
                self.logo_layout = item
            elif isinstance(item, QtWidgets.QLabel):
                self.logo_label = item

        self.logo_label.setToolTip(
            LOGO_INFO.format(
                self.logo_minimum_width,
                "/".join(self.logo_formats),
                "/".join(self.logo_background),
            )
        )

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
            None,
            "Seleziona immagine",
            "",
            "Immagini (*.png *.jpg *.bmp *.gif);;Tutti i file (*)",
        )

        if file_name:
            if self.__check_selected_logo(file_name):
                self.logo_path.setText(file_name)

                data = ""
                with open(file_name, "rb") as file:
                    data = file.read()
                    self.__set_logo_preview(data)
            else:
                self.__unset_logo_preview()

    def __validate_input(self, text):
        valid_text = self.__remove_chars(text)
        self.name.setEditText(valid_text)
        self.set_case_information()

    def __remove_chars(self, text):
        valid_characters = string.ascii_letters + string.digits + "_-"
        valid_text = "".join(c for c in text if c.lower() in valid_characters)
        return valid_text

    def set_index_from_type_proceedings_id(self, type_proceedings_id):
        self.proceeding_type.setCurrentIndex(
            self.proceeding_type.findData(type_proceedings_id)
        )

    def set_index_from_case_id(self, case_id):
        self.name.setCurrentIndex(self.name.findData(case_id))

    def set_current_cases(self):
        self.name.clear()

        if self.__temporary is False:
            self.name.lineEdit().setPlaceholderText(SELECT_CASE_NAME)
            for case in self.cases:
                self.name.addItem(case["name"], case["id"])
            self.name.setCurrentIndex(-1)
        else:
            self.name.setPlaceholderText(SELECT_CASE_NAME)

    def __set_current_proceeding_type(self):
        self.proceeding_type.clear()
        self.proceeding_type.lineEdit().setPlaceholderText(SELECT_PROCEEDING_TYPE)
        self.proceeding_type.lineEdit().setReadOnly(True)

        for proceedings in self.proceedings:
            self.proceeding_type.addItem(proceedings["name"], proceedings["id"])

        self.proceeding_type.setCurrentIndex(-1)

    def __set_logo_preview(self, data):
        if self.logo_preview is None:
            self.logo_preview = QtWidgets.QLabel()
            self.logo_layout.insertWidget(0, self.logo_preview)

        if self.logo_preview.isVisible() is False:
            self.logo_preview.setVisible(True)

        qp = QtGui.QPixmap()

        qp.loadFromData(data)

        self.logo_height = "auto"
        self.logo_width = "100"

        if qp.height() >= qp.width():
            self.logo_height = "50"
            self.logo_width = "auto"

        qp = qp.scaledToHeight(self.logo_path.height())
        self.logo_preview.setPixmap(qp)
        self.logo_path.setVisible(False)
        self.logo_button.setText(SELECT_FULL_LOGO)

    def __unset_logo_preview(self):
        if self.logo_preview is not None:
            self.logo_preview.setPixmap(QtGui.QPixmap())
            self.logo_preview.setVisible(False)

        self.logo_height = ""
        self.logo_width = ""
        self.logo_path.setText("")
        self.logo_path.setVisible(True)
        self.logo_button.setText(SELECT_EMPTY_LOGO)

    def set_case_information(self):
        if self.__temporary is False:
            current_text = self.name.currentText()
        else:
            current_text = self.name.text()

        case_info = next(
            (item for item in self.cases if item["name"] == current_text),
            None,
        )

        if case_info is not None:
            for keyword, value in case_info.items():
                if keyword == "logo_bin":
                    if value is not None:
                        self.__set_logo_preview(value)
                    else:
                        self.__unset_logo_preview()

                item = self.form.findChild(QtCore.QObject, keyword)

                if item is not None:
                    if isinstance(item, QtWidgets.QLineEdit) is not False:
                        if value is not None:
                            item.setText(str(value))
                    if isinstance(item, QtWidgets.QPlainTextEdit) is not False:
                        if value is not None:
                            item.setPlainText(str(value))
                    if isinstance(item, QtWidgets.QComboBox):
                        if keyword in "proceeding_type":
                            proceeding_type = next(
                                (
                                    proceeding
                                    for proceeding in self.proceedings
                                    if proceeding["id"] == value
                                ),
                                None,
                            )
                            if proceeding_type is not None:
                                value = proceeding_type["id"]
                            else:
                                value = -1

                            self.set_index_from_type_proceedings_id(value)
        else:
            self.__clear_case_information()

    def __clear_case_information(self):

        for item in self.form.children():
            if isinstance(item, QtWidgets.QLineEdit):
                item.setText("")
            elif isinstance(item, QtWidgets.QPlainTextEdit):
                item.setPlainText("")
            elif (
                isinstance(item, QtWidgets.QComboBox)
                and item.objectName() == "proceeding_type"
            ):
                item.setCurrentIndex(-1)

        self.__unset_logo_preview()

    def get_current_case_info(self):

        if self.__temporary is False:
            current_text = self.name.currentText()
        else:
            current_text = self.name.text()
        case_info = next(
            (item for item in self.cases if item["name"] == current_text), {}
        )

        for keyword in self.controller.keys:
            item = self.form.findChild(QtCore.QObject, keyword)

            if item is not None:
                if isinstance(item, QtWidgets.QComboBox):
                    if keyword in "name":
                        if self.__temporary is True:
                            item = self.name.text()
                        else:
                            item = self.name.currentText()

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

                elif isinstance(item, QtWidgets.QPlainTextEdit) is not False:
                    if item.toPlainText():
                        item = item.toPlainText()
                    else:
                        item = ""

                case_info[keyword] = item

        case_info["logo_height"] = self.logo_height
        case_info["logo_width"] = self.logo_width

        return case_info
