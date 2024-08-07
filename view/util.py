#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
import json
import subprocess
import base64
from datetime import datetime

from PyQt6 import QtCore, QtWidgets, QtGui
from view.configuration import Configuration as ConfigurationView
from view.case_form_dialog import CaseFormDialog
from view.dialog import Dialog, DialogButtonTypes
from view.tasks.tasks_info import TasksInfo
from view.configurations.screen_recorder_preview.screen_recorder_preview import (
    ScreenRecorderPreview,
)

from common.utility import get_platform
from common.constants import logger, details

from common.constants.view import case
from common.constants.view import verify_pec, verify_pdf_timestamp
from common.constants.view.tasks import status
from enum import Enum


class VerificationTypes(Enum):
    TIMESTAMP = 1
    PEC = 2


def validate_mail(mail):
    email_validator = QtGui.QRegularExpressionValidator(
        QtCore.QRegularExpression("[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
    )
    state = email_validator.validate(mail, 0)
    return bool(state[0] == QtGui.QRegularExpressionValidator.State.Acceptable)


def enable_all(items, enable):
    for item in items:
        if (
            isinstance(item, QtWidgets.QLabel)
            or isinstance(item, QtWidgets.QDateEdit)
            or isinstance(item, QtWidgets.QLineEdit)
            or isinstance(item, QtWidgets.QPushButton)
            or isinstance(item, QtWidgets.QTreeView)
        ):
            item.setEnabled(enable)


def screenshot_filename(path, basename, extention=".png"):
    return os.path.join(
        path,
        basename + "_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f") + extention,
    )


def show_case_info_dialog(case_info):
    CaseFormDialog(case_info).exec()


def show_configuration_dialog():
    ConfigurationView().exec()


def show_acquisition_info_dialog():
    TasksInfo().exec()


def show_screen_recorder_preview_dialog():
    ScreenRecorderPreview().exec()


def show_finish_acquisition_dialog(acquisition_directory):

    dialog = Dialog(
        logger.ACQUISITION_FINISHED,
        details.ACQUISITION_FINISHED,
    )
    dialog.message.setStyleSheet("font-size: 13px;")
    dialog.set_buttons_type(DialogButtonTypes.QUESTION)
    dialog.right_button.clicked.connect(dialog.close)
    dialog.left_button.clicked.connect(
        lambda: __open_acquisition_directory(dialog, acquisition_directory)
    )

    dialog.exec()


def __open_acquisition_directory(dialog, acquisition_directory):
    platform = get_platform()
    if platform == "win":
        os.startfile(acquisition_directory)
    elif platform == "osx":
        subprocess.call(["open", acquisition_directory])
    else:
        subprocess.call(["xdg-open", acquisition_directory])

    dialog.close()


def get_case_info(acquisition_directory):
    file = os.path.join(acquisition_directory, "caseinfo.json")
    case_info = {}

    if os.path.isfile(file):
        with open(file, "r") as f:
            case_info = json.load(f)
            logo_bin = case_info.get("logo_bin")
        if logo_bin:
            case_info["logo_bin"] = base64.b64decode(bytes(logo_bin, "utf-8"))
    else:
        dialog = Dialog(
            case.TITLE,
            case.WAR_NOT_CASE_INFO_JSON_FILE_FOUND,
        )
        dialog.message.setStyleSheet("font-size: 13px;")
        dialog.set_buttons_type(DialogButtonTypes.QUESTION)
        dialog.right_button.clicked.connect(
            lambda: __get_temporary_case_info(dialog, case_info, False)
        )
        dialog.left_button.clicked.connect(
            lambda: __get_temporary_case_info(dialog, case_info, True)
        )

        dialog.exec()

    return case_info


def __get_temporary_case_info(dialog, case_info, temporary=False):

    dialog.close()
    __case_info = {
        "name": "Unknown",
        "operator": "",
        "courthouse": "",
        "notes": "",
        "logo": "",
        "logo_width": "",
        "lawyer_name": "",
        "proceeding_type": 0,
        "proceeding_number": "",
        "logo_bin": None,
        "logo_height": "",
    }

    if temporary:
        case_form = CaseFormDialog(temporary=True)
        return_value = case_form.exec()
        if return_value:
            __case_info = case_form.get_case_info()
            if os.path.isfile(__case_info.get("logo")):
                __case_info["logo_bin"] = __set_logo_bin(__case_info.get("logo"))
            else:
                __case_info["logo_bin"] = None

    case_info.update(__case_info)


def __set_logo_bin(file_path):
    with open(file_path, "rb") as file:
        return file.read()


def show_finish_verification_dialog(path, verification_type):

    title = verify_pdf_timestamp.VERIFICATION_COMPLETED
    msg = verify_pec.VERIFY_PEC_SUCCESS_MSG

    if verification_type == VerificationTypes.TIMESTAMP:
        msg = verify_pdf_timestamp.VALID_TIMESTAMP_REPORT

    dialog = Dialog(
        title,
        msg,
    )
    dialog.message.setStyleSheet("font-size: 13px;")
    dialog.set_buttons_type(DialogButtonTypes.QUESTION)
    dialog.right_button.clicked.connect(dialog.close)
    dialog.left_button.clicked.connect(
        lambda: __open_verification_report(dialog, path, verification_type)
    )

    dialog.exec()


def __open_verification_report(dialog, path, verification_type):

    dialog.close()

    filename = "report_integrity_pec_verification.pdf"

    if verification_type == VerificationTypes.TIMESTAMP:
        filename = "report_timestamp_verification.pdf"

    pdf_file = os.path.join(path, filename)

    platform = get_platform()
    if platform == "win":
        os.startfile(pdf_file)
    elif platform == "osx":
        subprocess.call(["open", pdf_file])
    else:
        subprocess.call(["xdg-open", pdf_file])


def get_verification_label_text(
    verification_name, verification_status, verification_message
):
    __status = (
        '<strong style="color:green">{}</strong>'.format(verification_status)
        if verification_status == status.SUCCESS
        else '<strong style="color:red">{}</strong>'.format(verification_status)
    )
    __message = (
        "" if verification_message == "" else "details: {}".format(verification_message)
    )

    return "{}: {} {}".format(verification_name, __status, __message)


def add_label_in_verification_status_list(
    status_list: QtWidgets.QListWidget, label_text: str
):
    item = QtWidgets.QListWidgetItem(status_list)
    label = QtWidgets.QLabel(label_text)
    label.setWordWrap(True)
    item.setSizeHint(label.sizeHint())
    status_list.addItem(item)
    status_list.setItemWidget(item, label)
