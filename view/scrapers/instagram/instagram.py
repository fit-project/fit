# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os
import subprocess
import logging
from PyQt6 import QtCore, QtGui, QtWidgets


from view.scrapers.instagram.login_form import InstagramLoginForm
from view.scrapers.instagram.acquisition_form import InstagramAcquisitionForm
from view.scrapers.instagram.acquisition import InstagramAcquisition

from view.menu_bar import MenuBar as MenuBarView
from view.spinner import Spinner

from controller.case import Case as CaseController

from common.utility import get_platform, resolve_path

from common.constants.view.tasks import status
from common.constants import details, logger
from common.constants.view import general, instagram


class Instagram(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Instagram, self).__init__(*args, **kwargs)
        self.spinner = Spinner()

    def init(self, case_info, wizard, options=None):
        self.acquisition_directory = None
        self.is_task_started = False
        self.is_acquisition_running = False
        self.case_info = case_info
        self.wizard = wizard

        self.setWindowIcon(
            QtGui.QIcon(os.path.join(resolve_path("assets/svg/"), "FIT.svg"))
        )

        # set font
        font = QtGui.QFont()
        font.setPointSize(10)

        self.setObjectName("mainWindow")
        self.width = 530
        self.height = 480
        self.setFixedSize(self.width, self.height)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setStyleSheet(
            "QWidget {background-color: rgb(255, 255, 255);}"
        )
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        #### - START MENU BAR - #####
        # Uncomment to disable native menubar on Mac
        self.menuBar().setNativeMenuBar(False)

        # This bar is common on all main window
        self.menu_bar = MenuBarView(self, self.case_info)

        # Add default menu on menu bar
        self.menu_bar.add_default_actions()
        self.setMenuBar(self.menu_bar)
        #### - END MENUBAR - #####

        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(517, 340, 131, 23))
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setHidden(True)
        self.status.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.status)

        self.configuration_general = self.menu_bar.configuration_view.get_tab_from_name(
            "configuration_general"
        )

        # Get timestamp parameters
        self.configuration_timestamp = (
            self.menu_bar.configuration_view.get_tab_from_name(
                "configuration_timestamp"
            )
        )

        self.login_form = InstagramLoginForm(self.centralwidget)
        self.login_form.login_button.clicked.connect(self.__login)

        self.acquisition_form = InstagramAcquisitionForm(self.centralwidget)
        self.acquisition_form.scrape_button.clicked.connect(self.__scrape)

        self.retranslateUi()

        # ACQUISITION
        self.is_acquisition_running = False
        self.acquisition_manager = InstagramAcquisition(
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

        self.acquisition_manager.post_acquisition_is_finished.connect(
            self.__acquisition_is_finished
        )

    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)

    def __login(self):
        self.__enable_all(False)
        self.__start_spinner()
        self.login_form.enable_login(False)

        if self.is_task_started is False:
            self.__start_task()
        else:
            self.acquisition_manager.options["auth_info"] = {
                "username": self.login_form.input_username.text(),
                "password": self.login_form.input_password.text(),
                "profile": self.login_form.input_profile.text(),
            }

            self.acquisition_manager.login()

    def __is_logged_in(self, __status, __account_type):
        self.spinner.stop()
        self.__enable_all(True)

        if __status == status.SUCCESS:
            self.login_form.enable_login(False)
            self.__enable_acquisition_checkbox_from_account_type(__account_type)
        else:
            self.login_form.enable_login(True)

    def __start_task(self):
        if self.acquisition_directory is None:
            # Create acquisition directory
            self.acquisition_directory = CaseController().create_acquisition_directory(
                "instagram",
                self.configuration_general.configuration["cases_folder_path"],
                self.case_info["name"],
                self.login_form.input_profile.text(),
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
        checkboxes = self.acquisition_form.acquisition_group_box.findChildren(
            QtWidgets.QCheckBox
        )

        checkbox = next(
            filter(lambda checkbox: checkbox.text() == instagram.SAVED, checkboxes),
            None,
        )

        if account_type == 1:
            self.acquisition_form.enable_acquisition(True)
        elif account_type == 2 or account_type == 4:
            checkbox.setEnabled(False)
            self.acquisition_form.enable_acquisition(True)
        else:
            self.acquisition_form.enable_acquisition(False)

    def __scrape(self):
        self.is_acquisition_running = True
        self.progress_bar.setHidden(False)
        self.__enable_all(False)
        self.__start_spinner()
        self.acquisition_form.enable_acquisition(False)

        methods_to_execute = ["scrape_profile_picture", "scrape_info"]
        checkboxes = self.acquisition_form.acquisition_group_box.findChildren(
            QtWidgets.QCheckBox
        )
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
        self.login_form.enable_login(True)
        self.acquisition_form.enable_acquisition(False)

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

    def __handle_progress(self):
        self.progress_bar.setValue(self.progress_bar.value() + int(self.increment))

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

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
