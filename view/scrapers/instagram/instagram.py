# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os
import logging
from PyQt6 import QtCore, QtWidgets, uic

from view.scrapers.instagram.acquisition import InstagramAcquisition

from view.spinner import Spinner

from controller.case import Case as CaseController

from controller.configurations.tabs.general.general import (
    General as GeneralConfigurationController,
)

from view.util import (
    show_configuration_dialog,
    show_case_info_dialog,
    show_finish_acquisition_dialog,
    show_acquisition_info_dialog,
)

from common.utility import resolve_path, get_version

from common.constants.view.tasks import status
from common.constants.view import instagram


class Instagram(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Instagram, self).__init__(*args, **kwargs)
        self.spinner = Spinner()
        self.__init_ui()

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/instagram/instagram.ui"), self)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # CUSTOM TOP BAR
        self.left_box.mouseMoveEvent = self.move_window

        # MINIMIZE BUTTON
        self.minimize_button.clicked.connect(self.showMinimized)

        # CLOSE BUTTON
        self.close_button.clicked.connect(self.close)

        # CONFIGURATION BUTTON
        self.configuration_button.clicked.connect(show_configuration_dialog)

        # ACQUISITION INFO BUTTON
        self.acquisition_info.clicked.connect(show_acquisition_info_dialog)

        # HIDE PROGRESS BAR
        self.progress_bar.setValue(0)
        self.progress_bar.setHidden(True)

        # HIDE STATUS MESSAGE
        self.status_message.setHidden(True)

        # SET VERSION
        self.version.setText("v" + get_version())

        # SERVER INPUT FIELDS
        self.login_configuration_fields = self.login_configuration.findChildren(
            QtWidgets.QLineEdit
        )
        for field in self.login_configuration_fields:
            field.textChanged.connect(self.__enable_login_button)

        self.login_button.clicked.connect(self.__login)
        self.start_acquisition_button.clicked.connect(self.__start_acquisition)

        # ACQUISITION CRITERIA
        self.acquisition_criteria.setEnabled(False)
        # ACQUISITION STATUS
        self.acquisition_status.setEnabled(False)

        self.__uncheck_checkboxes()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_window(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def __enable_login_button(self):
        all_field_filled = all(
            input_field.text() for input_field in self.login_configuration_fields
        )
        self.login_button.setEnabled(all_field_filled)

    def __uncheck_checkboxes(self):
        for checkbox in self.acquisition_criteria.findChildren(QtWidgets.QCheckBox):
            if checkbox.isChecked():
                checkbox.setChecked(False)

    def init(self, case_info, wizard, options=None):
        self.acquisition_directory = None
        self.is_task_started = False
        self.is_acquisition_running = False
        self.case_info = case_info
        self.wizard = wizard

        self.case_button.clicked.connect(lambda: show_case_info_dialog(self.case_info))

        # ACQUISITION
        self.acquisition_manager = InstagramAcquisition(
            logging.getLogger(__name__),
            self.progress_bar,
            self.status_message,
            self,
        )

        self.acquisition_manager.start_tasks_is_finished.connect(
            self.__start_task_is_finished
        )

        self.acquisition_manager.logged_in.connect(self.__is_logged_in)

        self.acquisition_manager.progress.connect(self.__handle_progress)

        self.acquisition_manager.post_acquisition_is_finished.connect(
            self.__acquisition_is_finished
        )

        self.acquisition_manager.scraped_status.connect(self.__scraped_status)

    def __login(self):
        self.start_acquisition_button.setEnabled(True)
        self.acquisition_status.setEnabled(False)
        self.__uncheck_checkboxes()
        self.__enable_all(False)
        self.__start_spinner()
        self.progress_bar.setHidden(False)
        self.status_message.setHidden(False)
        self.acquisition_status_list.clear()

        if self.is_task_started is False:
            self.__start_task()
        else:
            self.acquisition_manager.options["auth_info"] = {
                "username": self.username.text(),
                "password": self.password.text(),
                "profile": self.profile_name.text(),
            }

            self.acquisition_manager.login()

    def __is_logged_in(self, __status, __account_type):
        self.spinner.stop()
        self.__enable_all(True)

        self.progress_bar.setHidden(True)
        self.status_message.setHidden(True)
        self.status_message.setText("")

        if __status == status.SUCCESS:
            self.login_configuration.setEnabled(False)
            self.__enable_acquisition_checkbox_from_account_type(__account_type)

    def __start_task(self):
        if self.acquisition_directory is None:
            # Create acquisition directory
            self.acquisition_directory = CaseController().create_acquisition_directory(
                "instagram",
                GeneralConfigurationController().configuration["cases_folder_path"],
                self.case_info["name"],
                self.profile_name.text(),
            )

        if self.acquisition_directory is not None:
            if self.is_task_started is False:
                self.acquisition_manager.options = {
                    "acquisition_directory": self.acquisition_directory,
                    "type": "instagram",
                    "case_info": self.case_info,
                }
                self.acquisition_manager.load_tasks()
                self.acquisition_manager.start()

    def __start_task_is_finished(self):
        self.is_task_started = True
        self.__login()

    def __enable_acquisition_checkbox_from_account_type(self, account_type):
        checkboxes = self.acquisition_criteria.findChildren(QtWidgets.QCheckBox)

        checkbox = next(
            filter(lambda checkbox: checkbox.text() == instagram.SAVED, checkboxes),
            None,
        )

        if account_type == 1:
            self.acquisition_criteria.setEnabled(True)
            self.acquisition_status.setEnabled(True)
        elif account_type == 2 or account_type == 4:
            self.scrape_saved_posts.setEnabled(False)
            self.acquisition_criteria.setEnabled(True)
            self.acquisition_status.setEnabled(True)

    def __start_acquisition(self):
        self.is_acquisition_running = True
        self.progress_bar.setHidden(False)
        self.status_message.setHidden(False)

        self.__enable_all(False)
        self.__start_spinner()

        methods_to_execute = ["scrape_profile_picture", "scrape_info"]
        checkboxes = self.acquisition_criteria.findChildren(QtWidgets.QCheckBox)

        checkboxes_checked = list(
            filter(lambda checkbox: checkbox.isChecked(), checkboxes)
        )
        for checkbox in checkboxes_checked:
            methods_to_execute.append(checkbox.objectName())

        self.acquisition_manager.options["methods_to_execute"] = methods_to_execute

        self.increment = 100 / len(methods_to_execute)

        # Create acquisition folder
        auth_info = self.acquisition_manager.options.get("auth_info")
        profile_dir = os.path.join(self.acquisition_directory, auth_info.get("profile"))
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)

        self.acquisition_manager.options["profile_dir"] = profile_dir
        self.acquisition_manager.scrape()

    def __acquisition_is_finished(self):
        self.spinner.stop()
        self.__enable_all(True)
        self.login_configuration.setEnabled(True)

        self.acquisition_criteria.setEnabled(False)
        self.acquisition_status.setEnabled(True)
        self.start_acquisition_button.setEnabled(False)
        self.scrape_saved_posts.setEnabled(True)

        self.acquisition_manager.log_end_message()
        self.acquisition_manager.set_completed_progress_bar()
        self.acquisition_manager.unload_tasks()

        show_finish_acquisition_dialog(self.acquisition_directory)

        self.progress_bar.setHidden(True)
        self.status_message.setHidden(True)
        self.status_message.setText("")

        self.acquisition_directory = None
        self.is_task_started = False
        self.is_acquisition_running = False

    def __handle_progress(self):
        self.progress_bar.setValue(self.progress_bar.value() + int(self.increment))

    def __scraped_status(self, info):

        __acquisition_name = None
        __method = info.get("method")

        if __method == "scrape_profile_picture":
            __acquisition_name = instagram.PROFILE_PIC
        elif __method == "scrape_info":
            __acquisition_name = [
                instagram.FULL_NAME,
                instagram.BIO,
                instagram.POST_NUMBER,
                instagram.ACCOUNT_TYPE,
            ]
        else:
            checkbox = self.acquisition_criteria.findChild(
                QtWidgets.QCheckBox, info.get("method")
            )

            if checkbox:
                __acquisition_name = checkbox.text()

        if __acquisition_name is not None:

            if isinstance(__acquisition_name, str):
                label_text = self.__get_acquisition_label_text(
                    __acquisition_name, info.get("status"), info.get("message")
                )
                self.__add_label_in_acquisition_status_list(label_text)

            if isinstance(__acquisition_name, list):
                for name in __acquisition_name:
                    label_text = self.__get_acquisition_label_text(
                        name, info.get("status"), info.get("message")
                    )
                    self.__add_label_in_acquisition_status_list(label_text)

    def __get_acquisition_label_text(
        self, acquisition_name, acquisition_status, acquisition_message
    ):
        __status = (
            '<strong style="color:green">{}</strong>'.format(acquisition_status)
            if acquisition_status == status.SUCCESS
            else '<strong style="color:red">{}</strong>'.format(acquisition_status)
        )
        __message = (
            ""
            if acquisition_message == ""
            else "details: {}".format(acquisition_message)
        )

        return "Acquisition {}: {} {}".format(acquisition_name, __status, __message)

    def __add_label_in_acquisition_status_list(self, label_text):
        item = QtWidgets.QListWidgetItem(self.acquisition_status_list)
        label = QtWidgets.QLabel(label_text)
        label.setWordWrap(True)
        item.setSizeHint(label.sizeHint())
        self.acquisition_status_list.addItem(item)
        self.acquisition_status_list.setItemWidget(item, label)

    def __enable_all(self, enable):
        self.setEnabled(enable)

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

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
