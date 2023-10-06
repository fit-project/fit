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

from configparser import SafeConfigParser

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWizard


from view.configuration import Configuration as ConfigurationView
from view.case_form import CaseForm as CaseFormView
from view.accordion import Accordion as AccordionView
from view.error import Error as ErrorView

from common.utility import resolve_path

from common.constants.view.wizard import *
from common.constants import error
from common.constants.view import wizard, general


class CaseInfoPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(CaseInfoPage, self).__init__(parent)
        self.setObjectName("CaseInfoPage")

        self.configuration_view = ConfigurationView(self)

        self.case_form_widget = QtWidgets.QWidget(self)
        self.case_form_widget.setGeometry(QtCore.QRect(0, 0, 795, 515))
        self.case_form_widget.setObjectName("case_form_widget")

        self.form = CaseFormView(self.case_form_widget)
        self.form.setGeometry(QtCore.QRect(0, 0, 400, 250))

        x = int((
            (self.case_form_widget.frameGeometry().width() / 2)
            - (self.form.frameGeometry().width() / 2)
            - 20
        ))
        y = int((self.case_form_widget.frameGeometry().height() / 2) - (
            self.form.frameGeometry().height() / 2
        ))
        self.form.move(x, y)

        self.configuration_button = QtWidgets.QPushButton(self)
        self.configuration_button.setGeometry(QtCore.QRect(400, 400, 100, 25))
        self.configuration_button.setObjectName("skip_button")
        self.configuration_button.setText("Configuration")
        self.configuration_button.clicked.connect(self.__configuration)

        # This allow to edit every row on combox
        self.form.name.setEditable(True)
        self.form.name.setCurrentIndex(-1)
        self.form.name.currentTextChanged.connect(self.completeChanged)
        self.form.case_form_layout.setWidget(
            0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.form.name
        )

    def isComplete(self):
        if self.form.name.findText(self.form.name.currentText()) >= 0:
            self.form.set_case_information()
        else:
            self.form.clear_case_information()
        return self.form.name.currentText() != ""

    def __configuration(self):
        self.configuration_view.exec()


class SelectTaskPage(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(SelectTaskPage, self).__init__(parent)

        self.assets_path = resolve_path("assets/images/wizard/")

        self.setObjectName("SelectTask")

        parser = SafeConfigParser()
        parser.read(resolve_path("assets/config.ini"))
        wizard_buttons = json.loads(parser.get("fit_properties", "wizard_buttons"))

        rows = 0
        index = 0
        for buttons in wizard_buttons:
            group = QtWidgets.QButtonGroup(self)
            group.buttonToggled[QtWidgets.QAbstractButton, bool].connect(
                self.completeChanged
            )

            group.buttonClicked.connect(self.__task_clicked)

            container = QtWidgets.QWidget(self)
            if rows == 0:
                container.setGeometry(QtCore.QRect(80, 40, 650, 112))
            elif rows == 1:
                container.setGeometry(QtCore.QRect(80, 160, 322, 112))

            hlayout = QtWidgets.QHBoxLayout(container)
            hlayout.setContentsMargins(0, 0, 0, 0)

            index = self.__add_task_buttons(buttons, group, container, hlayout, index)

            rows += 1

        # AREA RECAP INFO
        self.recap_case_box = AccordionView(CASE_SUMMARY, self)
        self.recap_case_box.setGeometry(QtCore.QRect(80, 400, 430, 30))
        self.recap_case_box_lay = QtWidgets.QVBoxLayout()

        self.recap_case_info = QtWidgets.QTextBrowser()
        self.recap_case_info.setGeometry(QtCore.QRect(30, 30, 430, 125))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.recap_case_info.setFont(font)
        self.recap_case_info.setReadOnly(True)
        self.recap_case_info.setObjectName("recap_case_info")

        self.recap_case_box_lay.addWidget(self.recap_case_info)
        self.recap_case_box.setContentLayout(self.recap_case_box_lay)

    def isComplete(self):
        is_complete = False

        if self.sender() and type(self.sender()) == QtWidgets.QButtonGroup:
            is_complete = True

        return is_complete

    def __add_task_buttons(self, buttons, group, container, hlayout, index):
        for button in buttons:
            wrapper = QtWidgets.QWidget(container)
            wrapper.setObjectName("radio_button_wrapper")
            wrapper.setStyleSheet(
                "QWidget#radio_button_wrapper {\n" "border: 1px solid black;\n" "}"
            )
            vlayout = QtWidgets.QVBoxLayout(wrapper)
            vlayout.setContentsMargins(5, 5, 5, 5)
            label = QtWidgets.QLabel(wrapper)
            label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            label.setPixmap(
                QtGui.QPixmap(
                    resolve_path(os.path.join(self.assets_path, button + ".png"))
                )
            )

            vlayout.addWidget(label)
            _button = QtWidgets.QRadioButton(wrapper)
            _button.setObjectName(button)
            vlayout.addWidget(_button)
            hlayout.addWidget(wrapper)
            group.addButton(_button, index)
            index += 1
        return index

    def __task_clicked(self):
        button_groups = [
            child for child in self.children() if type(child) == QtWidgets.QButtonGroup
        ]
        button_groups.remove(self.sender())

        for button_group in button_groups:
            if button_group.checkedButton() is not None:
                button_group.setExclusive(False)
                button_group.checkedButton().setChecked(False)
                button_group.setExclusive(True)


class Wizard(QtWidgets.QWizard):
    finished = QtCore.pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super(Wizard, self).__init__(parent)
        self.width = 800
        self.height = 600
        self.setObjectName("WizardView")
        self.case_info = {}

    def init_wizard(self):
        self.setFixedSize(self.width, self.height)
        self.setSizeGripEnabled(False)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setTitleFormat(QtCore.Qt.TextFormat.RichText)
        self.setSubTitleFormat(QtCore.Qt.TextFormat.RichText)
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )
        self.setWindowIcon(
            QtGui.QIcon(os.path.join(resolve_path("assets/svg/"), "FIT.svg"))
        )

        self.case_info_page = CaseInfoPage(self)
        self.select_task_page = SelectTaskPage(self)

        self.addPage(self.case_info_page)
        self.addPage(self.select_task_page)

        self.button(QtWidgets.QWizard.WizardButton.NextButton).clicked.connect(
            lambda: self.select_task_page.recap_case_info.setHtml(
                self._get_recap_case_info_HTML()
            )
        )

        self.button(QtWidgets.QWizard.WizardButton.FinishButton).clicked.connect(
            self._save_case
        )

        self.button(QtWidgets.QWizard.WizardButton.BackButton).clicked.connect(
            self.__back
        )

        self.button(QtWidgets.QWizard.WizardButton.FinishButton).setDisabled(True)

        self.setButtonText(
            QtWidgets.QWizard.WizardButton.FinishButton, general.BUTTON_START
        )
        self.setButtonText(
            QtWidgets.QWizard.WizardButton.CancelButton, general.BUTTON_EXIT
        )

        self.retranslateUi()

    def __back(self):
        self.case_info_page.form.set_case_information()

    def reload_case_info(self):
        self.case_info_page.form.set_case_information()
        self.select_task_page.recap_case_info.setHtml(self._get_recap_case_info_HTML())

    def _save_case(self):
        button_group = [
            child
            for child in self.select_task_page.children()
            if type(child) == QtWidgets.QButtonGroup and child.checkedButton()
        ]
        task = button_group[0].checkedButton().objectName()

        # store information case on the local DB
        try:
            if "id" in self.case_info:
                self.case_info_page.form.controller.cases = self.case_info
            else:
                self.case_info = self.case_info_page.form.controller.add(self.case_info)
                self.case_info_page.form.set_current_cases()
                self.case_info_page.form.set_index_from_case_id(self.case_info["id"])
        except Exception as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Warning,
                wizard.INSERT_UPDATE_CASE_INFO,
                error.INSERT_UPDATE_CASE_INFO,
                str(e),
            )
            error_dlg.exec()

        # Send signal to main loop to start the acquisition window
        self.finished.emit(task, self.case_info)

    def retranslateUi(self):
        self.setWindowTitle(self.__get_version())

        button_groups = self.select_task_page.findChildren(QtWidgets.QButtonGroup)
        if button_groups:
            for button_group in button_groups:
                for button in button_group.buttons():
                    taks = "TASK_" + button.objectName().upper()
                    button.setText(wizard.__dict__.get(taks))

    def __get_version(self):
        parser = SafeConfigParser()
        parser.read(resolve_path("assets/config.ini"))
        version = parser.get("fit_properties", "version")

        return version

    def _get_recap_case_info_HTML(self):
        self.case_info = self.case_info_page.form.get_current_case_info()

        html = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
        html += "<html>\n"
        html += "<head>\n"
        html += '<meta name="qrichtext" content="1" />\n'
        html += '<style type="text/css">\n'
        html += "p, li { white-space: pre-wrap; }\n"
        html += "</style>\n"
        html += "</head>\n"
        html += '<body style=" font-size:10pt; font-weight:400; font-style:normal;">\n'
        for keyword in self.case_info_page.form.controller.keys:
            item = self.findChild(QtWidgets.QLabel, keyword + "_label")
            if item is not None:
                value = self.case_info[keyword]
                if value is None or value == "":
                    value = "N/A"
                if keyword in "proceeding_type":
                    type_proceeding = next(
                        (
                            proceeding
                            for proceeding in self.case_info_page.form.proceedings
                            if proceeding["id"] == value
                        ),
                        None,
                    )
                    if type_proceeding is not None:
                        value = type_proceeding["name"]
                    else:
                        value = "N/A"

                label = item.text()
                html += '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; line-height:19px;">\n'
                html += (
                    '<span style=" font-size:14px; font-weight:300; color:#000000;">'
                    + label
                    + ": </span>\n"
                )
                html += (
                    '<span style=" font-size:14px; font-weight:600;  color:#000000;">'
                    + str(value).replace("\n", "<br>")
                    + "</span>\n"
                )
                html += "</p>\n"
        html += "</body>\n"
        html += "</html>"

        return html
