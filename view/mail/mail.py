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

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QFont, QIcon


from view.mail.login_form import MailLoginForm
from view.mail.search_form import MailSearchForm

from view.mail.acquisition import MailAcquisition
from view.menu_bar import MenuBar as MenuBarView
from view.error import Error as ErrorView
from view.spinner import Spinner

from common.utility import resolve_path
from common.utility import get_platform

from common.constants.view.tasks import status
from common.constants import error, details

from common.constants.view import mail, general
from common.constants.view.pec import search_pec
from common.constants.view.web import *
from common.constants import logger


class Mail(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Mail, self).__init__(*args, **kwargs)
        self.spinner = Spinner()

    def init(self, case_info, wizard, options=None):
        self.acquisition_directory = None
        self.is_task_started = False
        self.is_acquisition_running = False
        self.case_info = case_info
        self.wizard = wizard

        self.width = 990
        self.height = 590
        self.setFixedSize(self.width, self.height)

        self.setWindowIcon(QIcon(os.path.join(resolve_path("assets/svg/"), "FIT.svg")))
        self.setObjectName("email_scrape_window")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet(
            "QWidget {background-color: rgb(255, 255, 255);}"
        )

        # set font
        font = QFont()
        font.setPointSize(10)

        #### - START MENU BAR - #####
        # Uncomment to disable native menubar on Mac
        self.menuBar().setNativeMenuBar(False)

        # This bar is common on all main window
        self.menu_bar = MenuBarView(self, self.case_info)

        # Add default menu on menu bar
        self.menu_bar.add_default_actions()
        self.setMenuBar(self.menu_bar)
        #### - END MENUBAR - #####

        # PROGRESS BAR
        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximumWidth(400)
        self.progress_bar.setFixedHeight(25)
        self.status.addPermanentWidget(self.progress_bar)

        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStatusBar(self.status)
        self.progress_bar.setHidden(True)

        # SCRAPED EMAILS TREE
        layout = QtWidgets.QVBoxLayout()
        self.emails_tree = QtWidgets.QTreeWidget(self.centralwidget)
        self.emails_tree.setGeometry(QRect(510, 25, 440, 470))
        self.emails_tree.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.NoSelection
        )
        self.emails_tree.itemChanged.connect(self.__on_item_changed)

        self.emails_tree.setObjectName("emails_tree")
        self.emails_tree.setFont(font)

        self.emails_tree.setHeaderLabel(mail.IMAP_FOUND_EMAILS)
        self.root = QtWidgets.QTreeWidgetItem([mail.IMAP_FOLDERS])
        self.emails_tree.addTopLevelItem(self.root)
        layout.addWidget(self.emails_tree)

        self.login_form = MailLoginForm(self.centralwidget)
        self.login_form.login_button.clicked.connect(self.__login)

        self.search_form = MailSearchForm(self.centralwidget)
        self.search_form.search_button.clicked.connect(self.__search)

        self.setCentralWidget(self.centralwidget)

        # DOWNLOAD BUTTON
        self.download_button = QtWidgets.QPushButton(self)
        self.download_button.setGeometry(QRect(875, 525, 75, 25))
        self.download_button.clicked.connect(self.__download)
        self.download_button.setFont(font)
        self.download_button.setObjectName("StartAction")
        self.download_button.setEnabled(False)

        self.configuration_general = self.menu_bar.configuration_view.get_tab_from_name(
            "configuration_general"
        )

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

        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.download_button.setText(search_pec.DOWNLOAD_BUTTON)

    def __login(self):
        self.__enable_all(False)
        self.__start_spinner()

        if self.is_task_started is False:
            self.__start_task()
        else:
            self.acquisition_manager.options["auth_info"] = {
                "server": self.login_form.input_server.text(),
                "port": self.login_form.input_port.text(),
                "email": self.login_form.input_email.text(),
                "password": self.login_form.input_password.text(),
            }

            self.acquisition_manager.login()

    def __is_logged_in(self, __status):
        self.spinner.stop()
        self.__enable_all(True)

        if __status == status.SUCCESS:
            self.login_form.enable_login(False)
            self.search_form.enable_search(True)
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Information,
                mail.LOGIN_SUCCESS,
                mail.LOGIN_SUCCESS_MSG,
                "",
            )
            error_dlg.exec()

    def __start_task(self):
        if self.acquisition_directory is None:
            # Create acquisition directory
            self.acquisition_directory = (
                self.menu_bar.case_view.form.controller.create_acquisition_directory(
                    "email",
                    self.configuration_general.configuration["cases_folder_path"],
                    self.case_info["name"],
                    self.login_form.input_email.text(),
                )
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
        self.__enable_all(False)
        self.__start_spinner()

        from_date = self.search_form.input_from_date.date()
        to_date = self.search_form.input_to_date.date()
        selected_from_date = from_date.toPyDate()
        selected_to_date = to_date.toPyDate()
        selected_to_date = selected_to_date + timedelta(days=1)

        self.acquisition_manager.options["search_criteria"] = {
            "sender": self.search_form.input_from.text(),
            "recipient": self.search_form.input_to.text(),
            "subject": self.search_form.input_subject.text(),
            "from_date": selected_from_date,
            "to_date": selected_to_date,
        }

        self.acquisition_manager.search()

    def __search_emails_finished(self, __status, emails):
        self.spinner.stop()
        self.__enable_all(True)
        if __status == status.SUCCESS:
            if len(emails) == 0:
                error_dlg = ErrorView(
                    QtWidgets.QMessageBox.Icon.Information,
                    mail.NO_EMAILS,
                    error.NO_EMAILS,
                    details.RETRY,
                )
                error_dlg.exec()
            else:
                self.__add_emails_on_tree_widget(emails)
                self.emails_tree.expandAll()

    def __add_emails_on_tree_widget(self, emails):
        for key in emails:
            self.folder_tree = QtWidgets.QTreeWidgetItem([key])
            self.folder_tree.setData(
                0, Qt.ItemDataRole.UserRole, key
            )  # add identifier to the tree items
            self.folder_tree.setCheckState(0, Qt.CheckState.Unchecked)
            self.root.addChild(self.folder_tree)

            for value in emails[key]:
                sub_item = QtWidgets.QTreeWidgetItem([value])
                sub_item.setData(0, Qt.ItemDataRole.UserRole, key)
                sub_item.setCheckState(0, Qt.CheckState.Unchecked)
                self.folder_tree.addChild(sub_item)

        self.emails_tree.expandItem(self.root)

    def __is_checked(self):
        for i in range(self.root.childCount()):
            parent = self.root.child(i)
            for k in range(parent.childCount()):
                child = parent.child(k)
                if (
                    child.checkState(0) == Qt.CheckState.Checked
                    and self.download_button.isEnabled() is False
                ):
                    self.download_button.setEnabled(True)
                    self.search_form.search_button.setEnabled(False)
            if (
                parent.checkState(0) == Qt.CheckState.Checked
                and self.download_button.isEnabled() is False
            ):
                parent.setCheckState(0, Qt.CheckState.Unchecked)

    def __on_item_changed(self, item, column):
        child_count = item.childCount()
        for i in range(child_count):
            child = item.child(i)
            child.setCheckState(column, item.checkState(column))

        self.download_button.setEnabled(False)
        self.search_form.search_button.setEnabled(True)
        self.__is_checked()

    def __download(self):
        self.__enable_all(False)
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
                if email.checkState(0) == Qt.CheckState.Checked:
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
        self.__enable_all(True)
        self.login_form.enable_login(True)
        self.search_form.enable_search(False)
        self.download_button.setEnabled(False)
        self.emails_tree.clear()
        self.root = QtWidgets.QTreeWidgetItem([mail.IMAP_FOLDERS])
        self.emails_tree.addTopLevelItem(self.root)
        self.progress_bar.setHidden(True)
        self.status.showMessage("")
        self.acquisition_manager.log_end_message()
        self.acquisition_manager.set_completed_progress_bar()
        self.acquisition_manager.unload_tasks()

        self.__show_finish_acquisition_dialog()

        self.acquisition_directory = None
        self.is_task_started = False
        self.is_acquisition_running = False

    def __show_finish_acquisition_dialog(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(logger.ACQUISITION_FINISHED)
        msg.setText(details.ACQUISITION_FINISHED)
        msg.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No
        )

        return_value = msg.exec()
        if return_value == QtWidgets.QMessageBox.StandardButton.Yes:
            self.__open_acquisition_directory()

    def __open_acquisition_directory(self):
        platform = get_platform()
        if platform == "win":
            os.startfile(self.acquisition_directory)
        elif platform == "osx":
            subprocess.call(["open", self.acquisition_directory])
        else:  # platform == 'lin' || platform == 'other'
            subprocess.call(["xdg-open", self.acquisition_directory])

    def __enable_all(self, enable):
        self.setEnabled(enable)

    def __start_spinner(self):
        center_x = self.x() + self.width / 2
        center_y = self.y() + self.height / 2
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
