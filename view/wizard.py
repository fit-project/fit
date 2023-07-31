#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os

from configparser import SafeConfigParser

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWizard

from common.constants import error
from common.constants.view import wizard, general
from view.configuration import Configuration as ConfigurationView
from view.case_form import CaseForm as CaseFormView
from view.accordion import Accordion as AccordionView
from view.error import Error as ErrorView

from common.constants.view.wizard import *


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

        x = (
            (self.case_form_widget.frameGeometry().width() / 2)
            - (self.form.frameGeometry().width() / 2)
            - 20
        )
        y = (self.case_form_widget.frameGeometry().height() / 2) - (
            self.form.frameGeometry().height() / 2
        )
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

        self.setObjectName("SelectTask")

        # Create a button group for radio buttons
        self.radio_button_group1 = QtWidgets.QButtonGroup(self)
        self.radio_button_group1.setObjectName("radio_button_group1")
        self.radio_button_group1.buttonToggled[QtWidgets.QAbstractButton, bool].connect(
            self.completeChanged
        )
        self.radio_button_container = QtWidgets.QWidget(self)
        self.radio_button_container.setGeometry(QtCore.QRect(80, 40, 650, 112))
        self.radio_button_container.setObjectName("radio_button_container")
        self.radio_buttons_hlayout = QtWidgets.QHBoxLayout(self.radio_button_container)
        self.radio_buttons_hlayout.setContentsMargins(0, 0, 0, 0)
        self.radio_buttons_hlayout.setObjectName("radio_buttons_hlayout")

        self.radio_button_group1.buttonClicked.connect(self.__task_clicked)

        # RADIO BUTTON WEB
        self.web_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.web_radio_button_wrapper.setStyleSheet(
            "QWidget#web_radio_button_wrapper {\n" "border: 1px solid black;\n" "}"
        )
        self.web_radio_button_wrapper.setObjectName("web_radio_button_wrapper")
        self.web_vlayout = QtWidgets.QVBoxLayout(self.web_radio_button_wrapper)
        self.web_vlayout.setContentsMargins(5, 5, 5, 5)
        self.web_vlayout.setObjectName("web_vlayout")
        self.web_img = QtWidgets.QLabel(self.web_radio_button_wrapper)
        self.web_img.setStyleSheet("image: url(assets/images/wizard/web.png);")
        self.web_img.setText("")
        self.web_img.setObjectName("web_img")
        self.web_vlayout.addWidget(self.web_img)
        self.web = QtWidgets.QRadioButton(self.web_radio_button_wrapper)
        self.web.setObjectName("web")
        self.web_vlayout.addWidget(self.web)
        self.radio_buttons_hlayout.addWidget(self.web_radio_button_wrapper)
        self.radio_button_group1.addButton(self.web, 0)

        # RADIO BUTTON MAIL
        self.mail_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.mail_radio_button_wrapper.setStyleSheet(
            "QWidget#mail_radio_button_wrapper {\n" "border: 1px solid black;\n" "}"
        )
        self.mail_radio_button_wrapper.setObjectName("mail_radio_button_wrapper")
        self.mail_vlayout = QtWidgets.QVBoxLayout(self.mail_radio_button_wrapper)
        self.mail_vlayout.setContentsMargins(5, 5, 5, 5)
        self.mail_vlayout.setObjectName("mail_vlayout")
        self.mail_img = QtWidgets.QLabel(self.mail_radio_button_wrapper)
        self.mail_img.setEnabled(True)
        self.mail_img.setStyleSheet("image: url(assets/images/wizard/mail.png);\n")
        self.mail_img.setText("")
        self.mail_img.setObjectName("mail_img")
        self.mail_vlayout.addWidget(self.mail_img)
        self.mail = QtWidgets.QRadioButton(self.mail_radio_button_wrapper)
        self.mail.setEnabled(True)
        self.mail.setObjectName("mail")
        self.mail_vlayout.addWidget(self.mail)
        self.radio_buttons_hlayout.addWidget(self.mail_radio_button_wrapper)
        self.radio_button_group1.addButton(self.mail, 1)

        # RADIO BUTTON INSTAGRAM
        self.insta_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.insta_radio_button_wrapper.setStyleSheet(
            "QWidget#insta_radio_button_wrapper {\n" "border: 1px solid black;\n" "}"
        )
        self.insta_radio_button_wrapper.setObjectName("insta_radio_button_wrapper")
        self.insta_vlayout = QtWidgets.QVBoxLayout(self.insta_radio_button_wrapper)
        self.insta_vlayout.setContentsMargins(5, 5, 5, 5)
        self.insta_vlayout.setObjectName("insta_vlayout")
        self.insta_img = QtWidgets.QLabel(self.insta_radio_button_wrapper)
        self.insta_img.setEnabled(True)
        self.insta_img.setStyleSheet("image: url(assets/images/wizard/instagram.png);")
        self.insta_img.setText("")
        self.insta_img.setObjectName("insta_img")
        self.insta_vlayout.addWidget(self.insta_img)
        self.insta = QtWidgets.QRadioButton(self.insta_radio_button_wrapper)
        self.insta.setEnabled(True)
        self.insta.setObjectName("insta")
        self.insta_vlayout.addWidget(self.insta)
        self.radio_buttons_hlayout.addWidget(self.insta_radio_button_wrapper)
        self.radio_button_group1.addButton(self.insta, 3)

        # RADIO BUTTON VIDEO
        self.video_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container)
        self.video_radio_button_wrapper.setStyleSheet(
            "QWidget#video_radio_button_wrapper {\n" "border: 1px solid black;\n" "}"
        )
        self.video_radio_button_wrapper.setObjectName("video_radio_button_wrapper")
        self.video_vlayout = QtWidgets.QVBoxLayout(self.video_radio_button_wrapper)
        self.video_vlayout.setContentsMargins(5, 5, 5, 5)
        self.video_vlayout.setObjectName("video_vlayout")
        self.video_img = QtWidgets.QLabel(self.video_radio_button_wrapper)
        self.video_img.setEnabled(True)
        self.video_img.setStyleSheet("image: url(assets/images/wizard/video.png);")
        self.video_img.setText("")
        self.video_img.setObjectName("video_img")
        self.video_vlayout.addWidget(self.video_img)
        self.video = QtWidgets.QRadioButton(self.video_radio_button_wrapper)
        self.video.setEnabled(True)
        self.video.setObjectName("video")
        self.video_vlayout.addWidget(self.video)
        self.radio_buttons_hlayout.addWidget(self.video_radio_button_wrapper)
        self.radio_button_group1.addButton(self.video, 3)

        # Create a button group for radio buttons
        self.radio_button_group2 = QtWidgets.QButtonGroup(self)
        self.radio_button_group2.setObjectName("radio_button_group_row2")
        self.radio_button_group2.buttonToggled[QtWidgets.QAbstractButton, bool].connect(
            self.completeChanged
        )
        self.radio_button_container2 = QtWidgets.QWidget(self)
        self.radio_button_container2.setGeometry(QtCore.QRect(80, 160, 322, 112))
        self.radio_button_container2.setObjectName("radio_button_container2")
        self.radio_buttons_hlayout2 = QtWidgets.QHBoxLayout(
            self.radio_button_container2
        )
        self.radio_buttons_hlayout2.setContentsMargins(0, 0, 0, 0)
        self.radio_buttons_hlayout2.setObjectName("radio_buttons_hlayout2")

        self.radio_button_group2.buttonClicked.connect(self.__task_clicked)

        # RADIO BUTTON VERIFY TIMESTAMP
        self.timestamp_radio_button_wrapper = QtWidgets.QWidget(
            self.radio_button_container2
        )
        self.timestamp_radio_button_wrapper.setStyleSheet(
            "QWidget#timestamp_radio_button_wrapper {\n"
            "border: 1px solid black;\n"
            "}"
        )
        self.timestamp_radio_button_wrapper.setObjectName(
            "timestamp_radio_button_wrapper"
        )
        self.timestamp_vlayout = QtWidgets.QVBoxLayout(
            self.timestamp_radio_button_wrapper
        )
        self.timestamp_vlayout.setContentsMargins(5, 5, 5, 5)
        self.timestamp_vlayout.setObjectName("timestamp_vlayout")
        self.timestamp_img = QtWidgets.QLabel(self.timestamp_radio_button_wrapper)
        self.timestamp_img.setEnabled(False)
        self.timestamp_img.setStyleSheet(
            "image: url(assets/images/wizard/timestamp.png);"
        )
        self.timestamp_img.setText("")
        self.timestamp_img.setObjectName("timestamp_img")
        self.timestamp_vlayout.addWidget(self.timestamp_img)
        self.timestamp = QtWidgets.QRadioButton(self.timestamp_radio_button_wrapper)
        self.timestamp.setEnabled(True)
        self.timestamp.setObjectName("timestamp")
        self.timestamp_vlayout.addWidget(self.timestamp)
        self.radio_buttons_hlayout2.addWidget(self.timestamp_radio_button_wrapper)
        self.radio_button_group2.addButton(self.timestamp, 5)

        # RADIO BUTTON VERIFY PEC
        self.pec_radio_button_wrapper = QtWidgets.QWidget(self.radio_button_container2)
        self.pec_radio_button_wrapper.setStyleSheet(
            "QWidget#pec_radio_button_wrapper {\n" "border: 1px solid black;\n" "}"
        )
        self.pec_radio_button_wrapper.setObjectName("pec_radio_button_wrapper")
        self.pec_vlayout = QtWidgets.QVBoxLayout(self.pec_radio_button_wrapper)
        self.pec_vlayout.setContentsMargins(5, 5, 5, 5)
        self.pec_vlayout.setObjectName("pec_vlayout")
        self.pec_img = QtWidgets.QLabel(self.pec_radio_button_wrapper)
        self.pec_img.setEnabled(False)
        self.pec_img.setStyleSheet("image: url(assets/images/wizard/email.png);")
        self.pec_img.setText("")
        self.pec_img.setObjectName("pec_img")
        self.pec_vlayout.addWidget(self.pec_img)
        self.pec = QtWidgets.QRadioButton(self.pec_radio_button_wrapper)
        self.pec.setEnabled(True)
        self.pec.setObjectName("pec")
        self.pec_vlayout.addWidget(self.pec)
        self.radio_buttons_hlayout2.addWidget(self.pec_radio_button_wrapper)
        self.radio_button_group2.addButton(self.pec, 6)

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
        return (
            self.radio_button_group1.checkedId() >= 0
            or self.radio_button_group2.checkedId() >= 0
        )

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
        self.setWindowIcon(QtGui.QIcon(os.path.join("assets/svg/", "FIT.svg")))

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
        self.select_task_page.web.setText(TASK_WEB)
        self.select_task_page.mail.setText(TASK_MAIL)
        self.select_task_page.insta.setText(TASK_INSTAGRAM)
        self.select_task_page.video.setText(TASK_VIDEO)
        self.select_task_page.timestamp.setText(TASK_VERIFY_TIMESTAMP)
        self.select_task_page.pec.setText(TASK_VERIFY_PEC)

    def __get_version(self):
        parser = SafeConfigParser()
        parser.read("assets/config.ini")
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
