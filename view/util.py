#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtCore, QtWidgets, QtGui
from configparser import ConfigParser
from common.utility import resolve_path


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


def get_version():
    parser = ConfigParser()
    parser.read(resolve_path("assets/config.ini"))
    version = parser.get("fit_properties", "tag_name")

    return version
