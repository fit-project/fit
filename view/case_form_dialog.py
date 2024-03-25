#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6 import QtCore, QtWidgets, uic

from view.case_form_manager import CaseFormManager


from common.utility import resolve_path

from controller.case import Case as CaseController
from common.constants.view.case import *


class CaseFormDialog(QtWidgets.QDialog):
    def __init__(self, case_info=None, parent=None):
        super(CaseFormDialog, self).__init__(parent)

        uic.loadUi(resolve_path("ui/case/dialog.ui"), self)

        self.case_info = case_info

        case_name = self.case_info.get("name")
        self.form_manager = CaseFormManager(self.findChild(QtWidgets.QFrame, "form"))

        self.name = self.findChild(QtWidgets.QComboBox, "name")
        self.name.setCurrentText(case_name)
        self.name.lineEdit().setReadOnly(True)

        if case_name not in self.form_manager.controller.names:
            self.form_manager.cases.append(self.case_info)

        id = -1
        if "id" in self.case_info:
            id = self.case_info.get("id")

        self.setWindowTitle(DIALOG_TITLE.format(case_name, str(id)))
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )

        self.form_manager.set_case_information()

    def accept(self) -> None:
        self.case_info = self.form_manager.get_current_case_info()
        CaseController().cases = self.case_info
        return super().accept()

    def reject(self) -> None:
        return super().reject()
