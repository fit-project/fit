#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
import subprocess
from datetime import datetime

from PyQt6 import QtCore, QtWidgets, QtGui
from view.configuration import Configuration as ConfigurationView
from view.case_form_dialog import CaseFormDialog
from view.dialog import Dialog, DialogButtonTypes
from view.tasks.tasks_info import TasksInfo

from common.utility import get_platform
from common.constants import logger, details


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
    else:  # platform == 'lin' || platform == 'other'
        subprocess.call(["xdg-open", acquisition_directory])

    dialog.close()
