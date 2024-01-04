#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from configparser import ConfigParser

from PyQt6 import QtCore, QtWidgets, uic


from view.configuration import Configuration as ConfigurationView
from view.case_form_manager import CaseFormManager
from view.case_form_dialog import CaseFormDialog
from view.error import Error as ErrorView

from common.utility import resolve_path

from common.constants.view.wizard import *
from common.constants import error
from common.constants.view import wizard, general


class Wizard(QtWidgets.QWizard):
    finished = QtCore.pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super(Wizard, self).__init__(parent)
        uic.loadUi(resolve_path("ui/wizard/wizard.ui"), self)

        self.task = None
        self.case_info = {}

        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )

        case_form_layout = self.findChild(QtWidgets.QFormLayout, "case_form_layout")
        self.form_manager = CaseFormManager(case_form_layout)

        self.name = self.findChild(QtWidgets.QComboBox, "name")
        self.name.currentTextChanged.connect(self.form_manager.set_case_information)

        self.case_info_page.registerField(
            "name*",
            self.name,
            "currentText",
            QtWidgets.QComboBox.currentTextChanged,
        )

        self.enable_finish_button = QtWidgets.QRadioButton(
            "completion_button", self.select_task_page
        )
        self.enable_finish_button.setHidden(True)

        self.buttons = self.findChildren(QtWidgets.QRadioButton)
        for button in self.buttons:
            button.clicked.connect(self.__task_clicked)

        self.select_task_page.registerField(
            "completion_button*",
            self.enable_finish_button,
            "checked",
            QtWidgets.QRadioButton.toggled,
        )

        self.configuration_button = self.findChild(
            QtWidgets.QPushButton, "configuration_button"
        )
        self.configuration_button.clicked.connect(self.__configuration)

        self.case_summary_button = self.findChild(
            QtWidgets.QPushButton, "case_summary_button"
        )
        self.case_summary_button.clicked.connect(self.__case_summary)

        self.button(QtWidgets.QWizard.WizardButton.NextButton).clicked.connect(
            self.__load_case_info
        )

        self.button(QtWidgets.QWizard.WizardButton.FinishButton).clicked.connect(
            self._save_case
        )

        self.button(QtWidgets.QWizard.WizardButton.BackButton).clicked.connect(
            self.__back
        )

        self.setButtonText(
            QtWidgets.QWizard.WizardButton.FinishButton, general.BUTTON_START
        )
        self.setButtonText(
            QtWidgets.QWizard.WizardButton.CancelButton, general.BUTTON_EXIT
        )

        self.retranslateUi()

    def reload_case_info(self):
        self.form_manager.set_case_information()

    def __configuration(self):
        ConfigurationView().exec()

    def __case_summary(self):
        CaseFormDialog(self.case_info).exec()

    def __load_case_info(self):
        self.case_info = self.form_manager.get_current_case_info()

    def __task_clicked(self):
        for button in self.buttons:
            if button.isChecked() and button != self.sender():
                button.setChecked(False)

        self.enable_finish_button.toggle()
        self.sender().toggle()
        self.task = self.sender().objectName()

    def __back(self):
        self.task = None
        for button in self.buttons:
            if button.isChecked():
                button.setChecked(False)

    def _save_case(self):
        # store information case on the local DB
        try:
            if "id" in self.case_info:
                self.form_manager.controller.cases = self.case_info
            else:
                self.case_info = self.form_manager.controller.add(self.case_info)
                self.form_manager.__set_current_cases()
                self.form_manager.set_index_from_case_id(self.case_info["id"])
        except Exception as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Warning,
                wizard.INSERT_UPDATE_CASE_INFO,
                error.INSERT_UPDATE_CASE_INFO,
                str(e),
            )
            error_dlg.exec()

        # Send signal to main loop to start the acquisition window
        self.finished.emit(self.task, self.case_info)

    def retranslateUi(self):
        self.setWindowTitle(self.windowTitle() + " " + self.__get_version())

    def __get_version(self):
        parser = ConfigParser()
        parser.read(resolve_path("assets/config.ini"))
        version = parser.get("fit_properties", "version")

        return version
