#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


import sys
from PyQt6 import QtCore, QtWidgets

from view.checks.check import Check
from view.error import Error as ErrorView
from common.utility import check_internet_connection

from common.constants.view.tasks import status
from common.constants.view.init import CHECK_CONNETION, ERR_INTERNET_DISCONNECTED


class NetworkCheck(Check):
    def __init__(self, parent=None):
        super().__init__(parent)

    def run_check(self):
        if check_internet_connection() is False:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                CHECK_CONNETION,
                ERR_INTERNET_DISCONNECTED,
                "",
            )
            error_dlg.message.setStyleSheet("font-size: 13px;")
            error_dlg.right_button.clicked.connect(
                lambda: self.finished.emit(status.FAIL)
            )

            error_dlg.exec()
        else:
            self.finished.emit(status.SUCCESS)
