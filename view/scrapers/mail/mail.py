#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


import os
import logging
import subprocess

from datetime import timedelta
from PyQt6 import QtCore, QtWidgets, QtGui, uic


from view.scrapers.mail.acquisition import MailAcquisition
from view.scrapers.mail.clickable_label import ClickableLabel
from view.dialog import Dialog, DialogButtonTypes

from view.error import Error as ErrorView
from view.spinner import Spinner

from view.util import validate_mail, enable_all, get_version

from controller.configurations.tabs.general.general import (
    General as GeneralConfigurationTab,
)
from controller.case import Case as CaseController

from common.utility import resolve_path
from common.utility import get_platform

from common.constants.view.tasks import status
from common.constants import error, details

from common.constants.view import mail, general
from common.constants.view.pec import search_pec
from common.constants.view.web import *
from common.constants import logger


from ui.mail import resources


class Mail(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(Mail, self).__init__(parent)
        self.is_valid_mail = False
        self.spinner = Spinner()

        self.__init_ui()

    def __init_ui(self):

        uic.loadUi(resolve_path("ui/mail/mail.ui"), self)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # GET CUSTOM BAR
        self.custom_bar = self.findChild(QtWidgets.QFrame, "leftBox")
        self.custom_bar.mouseMoveEvent = self.move_window

        # SETTING BUTTON
        self.configuration_button = self.findChild(
            QtWidgets.QPushButton, "settingsTopButton"
        )
        # self.configuration_button.clicked.connect(self.__configuration)

        # MINIMIZE BUTTON
        self.minimize_app_button = self.findChild(
            QtWidgets.QPushButton, "minimizeButton"
        )
        self.minimize_app_button.clicked.connect(lambda: self.showMinimized())

        # CLOSE BUTTON
        self.close_app_button = self.findChild(QtWidgets.QPushButton, "closeButton")
        self.close_app_button.clicked.connect(lambda: self.close())

        # PROGRESS BAR
        self.progress_bar = self.findChild(QtWidgets.QProgressBar, "progress_bar")
        self.progress_bar.hide()

        # STATUS MESSAGE
        self.status = self.findChild(QtWidgets.QLabel, "status_message")
        self.status.hide()

        # SET VERSION
        self.version = self.findChild(QtWidgets.QLabel, "version")
        self.version.setText("v" + get_version())

        # SERVER CONFIGURATION
        self.server_configuration = self.findChild(
            QtWidgets.QFrame, "server_configuration"
        )

        self.server_configuration_vlayout = self.findChild(
            QtWidgets.QVBoxLayout, "server_configuration_vlayout"
        )

        self.label_two_factor_auth = ClickableLabel()
        self.server_configuration_vlayout.addWidget(self.label_two_factor_auth)

        # SERVER INPUT FIELDS
        self.server_configuration_fields = self.server_configuration.findChildren(
            QtWidgets.QLineEdit
        )
        for field in self.server_configuration_fields:
            field.textChanged.connect(self.__enable_login_button)
            if field.objectName() == "server_port":
                field.setValidator(QtGui.QIntValidator())
            elif field.objectName() == "server_name":
                field.textEdited.connect(self.__validate_input)

        # LOGIN BUTTON
        self.login_button = self.server_configuration.findChild(QtWidgets.QPushButton)
        self.login_button.clicked.connect(self.__login)
        self.login_button.setEnabled(False)

        # SEARCH CRITERIA
        self.search_criteria = self.findChild(QtWidgets.QFrame, "search_criteria")
        enable_all(self.search_criteria.children(), False)

        # SEARCH DATE FROM
        self.search_date_from = self.search_criteria.findChild(
            QtWidgets.QDateEdit, "search_date_from"
        )
        self.search_date_from.setDate(QtCore.QDate.currentDate().addDays(-14))

        # SEARCH DATE TO
        self.search_date_to = self.search_criteria.findChild(
            QtWidgets.QDateEdit, "search_date_to"
        )
        self.search_date_to.setDate(QtCore.QDate.currentDate())

        # SEARCH EMAIL FROM
        self.search_email_from = self.search_criteria.findChild(
            QtWidgets.QLineEdit, "search_email_from"
        )
        self.search_email_from.textChanged.connect(self.__is_valid_search_mail)
        self.search_email_from.editingFinished.connect(self.__enable_search_button)

        # SEARCH EMAIL TO
        self.search_email_to = self.search_criteria.findChild(
            QtWidgets.QLineEdit, "search_email_to"
        )
        self.search_email_to.textChanged.connect(self.__is_valid_search_mail)
        self.search_email_to.editingFinished.connect(self.__enable_search_button)

        # SEARCH EMAIL SUBJECT
        self.search_email_subject = self.search_criteria.findChild(
            QtWidgets.QLineEdit, "search_email_subject"
        )

        # SEARCH BUTTON
        self.search_button = self.search_criteria.findChild(QtWidgets.QPushButton)
        self.search_button.clicked.connect(self.__search)

        # EMAIL FOUNDED
        self.select_email = self.findChild(QtWidgets.QFrame, "select_email")
        enable_all(self.select_email.children(), False)
        self.emails_tree = self.select_email.findChild(QtWidgets.QTreeWidget)
        self.emails_tree.setHeaderLabel("")
        self.emails_tree.itemChanged.connect(self.__on_item_changed)

        # DOWNLOAD BUTTON
        self.download_button = self.select_email.findChild(QtWidgets.QPushButton)
        self.download_button.clicked.connect(self.__download)
        self.__retranslate_ui()

    def __retranslate_ui(self):
        self.download_button.setText(search_pec.DOWNLOAD_BUTTON)
        self.label_two_factor_auth.setText(mail.TWO_FACTOR_AUTH)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_window(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def init(self, case_info, wizard, options=None):
        self.acquisition_directory = None
        self.is_task_started = False
        self.is_acquisition_running = False
        self.case_info = case_info
        self.wizard = wizard

        self.acquisition_manager = MailAcquisition(
            logging.getLogger(__name__),
            self.progress_bar,
            self.status,
            self,
        )

        self.acquisition_manager.start_tasks_is_finished.connect(
            self.__start_task_is_finished
        )

        self.acquisition_manager.logged_in.connect(self.__is_logged_in)
        self.acquisition_manager.progress.connect(self.__handle_progress)
        self.acquisition_manager.search_emails_finished.connect(
            self.__search_emails_finished
        )
        self.acquisition_manager.post_acquisition_is_finished.connect(
            self.__acquisition_is_finished
        )

    def __login(self):
        enable_all(self.server_configuration.children(), False)
        self.__start_spinner()

        if self.is_task_started is False:
            self.__start_task()
        else:
            self.acquisition_manager.options["auth_info"] = {
                "server": self.server_configuration.findChild(
                    QtWidgets.QLineEdit, "server_name"
                ).text(),
                "port": self.server_configuration.findChild(
                    QtWidgets.QLineEdit, "server_port"
                ).text(),
                "email": self.server_configuration.findChild(
                    QtWidgets.QLineEdit, "login"
                ).text(),
                "password": self.server_configuration.findChild(
                    QtWidgets.QLineEdit, "password"
                ).text(),
            }

            self.acquisition_manager.login()

    def __is_logged_in(self, __status):
        self.spinner.stop()

        if __status == status.SUCCESS:
            enable_all(self.search_criteria.children(), True)
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Information,
                mail.LOGIN_SUCCESS,
                mail.LOGIN_SUCCESS_MSG,
                "",
            )
            error_dlg.exec()
        else:
            enable_all(self.server_configuration.children(), True)

    def __start_task(self):
        if self.acquisition_directory is None:
            # Create acquisition directory
            self.acquisition_directory = CaseController().create_acquisition_directory(
                "email",
                GeneralConfigurationTab().configuration["cases_folder_path"],
                self.case_info["name"],
                self.server_configuration.findChild(
                    QtWidgets.QLineEdit, "login"
                ).text(),
            )

        if self.acquisition_directory is not None:
            if self.is_task_started is False:
                self.acquisition_manager.options = {
                    "acquisition_directory": self.acquisition_directory,
                    "type": "email",
                    "case_info": self.case_info,
                }
                self.acquisition_manager.load_tasks()
                self.acquisition_manager.start()

    def __start_task_is_finished(self):
        self.is_task_started = True
        self.__login()

    def __search(self):
        enable_all(self.search_criteria.children(), False)
        self.__start_spinner()

        from_date = self.search_date_from.date()
        to_date = self.search_date_to.date()
        selected_from_date = from_date.toPyDate()
        selected_to_date = to_date.toPyDate()
        selected_to_date = selected_to_date + timedelta(days=1)

        self.acquisition_manager.options["search_criteria"] = {
            "sender": self.search_email_from.text(),
            "recipient": self.search_email_to.text(),
            "subject": self.search_email_subject.text(),
            "from_date": selected_from_date,
            "to_date": selected_to_date,
        }

        self.acquisition_manager.search()

    def __search_emails_finished(self, __status, emails):
        self.spinner.stop()
        if __status == status.SUCCESS:
            if len(emails) == 0:
                error_dlg = ErrorView(
                    QtWidgets.QMessageBox.Icon.Information,
                    mail.NO_EMAILS,
                    error.NO_EMAILS,
                    details.RETRY,
                )
                error_dlg.exec()
                enable_all(self.search_criteria.children(), True)
            else:
                enable_all(self.select_email.children(), True)
                self.download_button.setEnabled(False)
                self.__add_emails_on_tree_widget(emails)
                self.emails_tree.expandAll()
        else:
            enable_all(self.search_criteria.children(), True)

    def __add_emails_on_tree_widget(self, emails):
        self.emails_tree.setHeaderLabel(mail.IMAP_FOUND_EMAILS)
        self.root = QtWidgets.QTreeWidgetItem([mail.IMAP_FOLDERS])
        self.emails_tree.addTopLevelItem(self.root)

        for key in emails:
            self.folder_tree = QtWidgets.QTreeWidgetItem([key])
            self.folder_tree.setData(
                0, QtCore.Qt.ItemDataRole.UserRole, key
            )  # add identifier to the tree items
            self.folder_tree.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
            self.root.addChild(self.folder_tree)

            for value in emails[key]:
                sub_item = QtWidgets.QTreeWidgetItem([value])
                sub_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, key)
                sub_item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
                self.folder_tree.addChild(sub_item)

        self.emails_tree.expandItem(self.root)

    def __is_checked(self):
        for i in range(self.root.childCount()):
            parent = self.root.child(i)
            for k in range(parent.childCount()):
                child = parent.child(k)
                if (
                    child.checkState(0) == QtCore.Qt.CheckState.Checked
                    and self.download_button.isEnabled() is False
                ):
                    self.download_button.setEnabled(True)
            if (
                parent.checkState(0) == QtCore.Qt.CheckState.Checked
                and self.download_button.isEnabled() is False
            ):
                parent.setCheckState(0, QtCore.Qt.CheckState.Unchecked)

    def __on_item_changed(self, item, column):
        child_count = item.childCount()
        for i in range(child_count):
            child = item.child(i)
            child.setCheckState(column, item.checkState(column))

        self.download_button.setEnabled(False)
        self.__is_checked()

    def __download(self):
        enable_all(self.select_email.children(), False)
        self.__start_spinner()
        self.is_acquisition_running = True
        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(0)

        emails_to_download = {}

        emails_counter = 0
        for i in range(self.root.childCount()):
            folder = self.root.child(i)
            folder_name = folder.text(0)
            for k in range(folder.childCount()):
                email = folder.child(k)
                if email.checkState(0) == QtCore.Qt.CheckState.Checked:
                    emails_counter += 1
                    if folder_name in emails_to_download:
                        emails_to_download[folder_name].append(email.text(0))
                    else:
                        emails_to_download[folder_name] = [email.text(0)]

        self.increment = 100 / emails_counter
        self.acquisition_manager.options["emails_to_download"] = emails_to_download
        self.acquisition_manager.download()

    def __handle_progress(self):
        self.progress_bar.setValue(self.progress_bar.value() + int(self.increment))

    def __acquisition_is_finished(self):
        self.spinner.stop()
        enable_all(self.server_configuration.children(), True)
        self.emails_tree.clear()
        self.progress_bar.setHidden(True)
        self.status.setText("")
        self.acquisition_manager.log_end_message()
        self.acquisition_manager.set_completed_progress_bar()
        self.acquisition_manager.unload_tasks()

        self.__show_finish_acquisition_dialog()

        self.acquisition_directory = None
        self.is_task_started = False
        self.is_acquisition_running = False

    def __show_finish_acquisition_dialog(self):

        dialog = Dialog(
            logger.ACQUISITION_FINISHED,
            details.ACQUISITION_FINISHED,
        )
        dialog.message.setStyleSheet("font-size: 13px;")
        dialog.set_buttons_type(DialogButtonTypes.QUESTION)
        dialog.right_button.clicked.connect(dialog.close)
        dialog.left_button.clicked.connect(
            lambda: self.__open_acquisition_directory(dialog)
        )

        dialog.exec()

    def __open_acquisition_directory(self, dialog):
        platform = get_platform()
        if platform == "win":
            os.startfile(self.acquisition_directory)
        elif platform == "osx":
            subprocess.call(["open", self.acquisition_directory])
        else:  # platform == 'lin' || platform == 'other'
            subprocess.call(["xdg-open", self.acquisition_directory])

        dialog.close()

    def __is_valid_search_mail(self, text):
        self.is_valid_mail = validate_mail(text)
        self.search_button.setEnabled(False)
        if self.is_valid_mail is False:
            self.sender().setStyleSheet("border: 1px solid red;")
        else:
            self.sender().setStyleSheet("")
            self.search_button.setEnabled(True)

    def __enable_search_button(self):
        if self.sender().text() == "" and self.search_button.isEnabled() is False:
            self.is_valid_email = True
            self.sender().setStyleSheet("")
            self.search_button.setEnabled(True)

    def __enable_login_button(self, text):
        if self.sender().objectName() == "login":
            self.is_valid_mail = validate_mail(text)
            if self.is_valid_mail is False:
                self.sender().setStyleSheet("border: 1px solid red;")
            else:
                self.sender().setStyleSheet("")

        all_fields_filled = all(
            field.text() for field in self.server_configuration_fields
        )
        self.login_button.setEnabled(all_fields_filled and self.is_valid_mail)

    def __validate_input(self, text):
        sender = self.sender()
        sender.setText(text.replace(" ", ""))

    def __start_spinner(self):
        center_x = self.x() + self.width() / 2
        center_y = self.y() + self.height() / 2
        self.spinner.set_position(center_x, center_y)
        self.spinner.start()

    def __back_to_wizard(self):
        if self.is_acquisition_running is False:
            self.deleteLater()
            self.wizard.reload_case_info()
            self.wizard.show()
        else:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Warning,
                ACQUISITION_IS_RUNNING,
                WAR_ACQUISITION_IS_RUNNING,
                "",
            )
            error_dlg.exec()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
