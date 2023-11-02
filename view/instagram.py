# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
import os
import shutil
import logging
import subprocess
from common.constants.view.tasks import state, status
import common.utility
from PyQt6 import QtCore, QtGui, QtWidgets
from instaloader import (
    InvalidArgumentException,
    BadCredentialsException,
    ConnectionException,
    ProfileNotExistsException,
)

from view.menu_bar import MenuBar as MenuBarView
from view.error import Error as ErrorView
from view.spinner import Spinner
from view.acquisition.acquisition import Acquisition

from controller.instagram import Instagram as InstragramController

from common.utility import get_platform, resolve_path
from common.constants import (
    details as Details,
    logger as Logger,
    tasks,
    error as Error,
)
from common.constants.view import general, instagram, mail

logger_acquisition = logging.getLogger(__name__)


class InstagramWorker(QtCore.QObject):
    scraped = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(object)
    logged_in = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(
        self, instagram_controller, methods_to_execute, checkbox, acquisition_group_box
    ):
        super().__init__()
        self.checkbox = checkbox
        self.acquisition_group_box = acquisition_group_box
        self.instagram_controller = instagram_controller
        self.methods_to_execute = methods_to_execute

    @QtCore.pyqtSlot()
    def run(self):
        if self.instagram_controller.is_logged_in is False:
            try:
                self.instagram_controller.login()
            except InvalidArgumentException as e:
                self.error.emit(
                    {
                        "title": instagram.INVALID_USER,
                        "msg": Error.INVALID_USER,
                        "details": e,
                    }
                )
            except BadCredentialsException as e:
                self.error.emit(
                    {
                        "title": instagram.LOGIN_ERROR,
                        "msg": Error.PASSWORD_ERROR,
                        "details": e,
                    }
                )
            except ConnectionException as e:
                self.error.emit(
                    {
                        "title": instagram.CONNECTION_ERROR,
                        "msg": Error.LOGIN_ERROR,
                        "details": e,
                    }
                )
            except ProfileNotExistsException as e:
                self.error.emit(
                    {
                        "title": instagram.INVALID_PROFILE,
                        "msg": Error.INVALID_PROFILE,
                        "details": e,
                    }
                )
            except Exception as e:
                self.error.emit(e)
            else:
                check_account = self.instagram_controller.check_account()
                if check_account == 1:
                    self.acquisition_group_box.setEnabled(True)
                    pass
                elif check_account == 2 or check_account == 4:
                    self.checkbox[4].setEnabled(False)
                    self.acquisition_group_box.setEnabled(True)
                else:
                    self.acquisition_group_box.setEnabled(False)
                self.logged_in.emit()
        else:
            for checkbox, method in self.methods_to_execute:
                if checkbox:
                    method()
                    self.progress.emit()

            self.scraped.emit()

        self.finished.emit()


class Instagram(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Instagram, self).__init__(*args, **kwargs)
        self.acquisition_directory = None
        self.acquisition_is_started = False
        self.is_enabled_timestamp = False
        self.methods_to_execute = None
        self.spinner = Spinner()
        self.instagram_controller = InstragramController()
        self.username = None
        self.password = None
        self.profile = None
        self.login_time = None

    def init(self, case_info, wizard, options=None):
        self.__init__()
        self.wizard = wizard
        self.case_info = case_info

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

        self.configuration_general = self.menu_bar.configuration_view.get_tab_from_name(
            "configuration_general"
        )

        # Get timestamp parameters
        self.configuration_timestamp = (
            self.menu_bar.configuration_view.get_tab_from_name(
                "configuration_timestamp"
            )
        )

        # LOGIN CONFIGURATION GROUP BOX
        self.loging_configuration_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.loging_configuration_group_box.setEnabled(True)
        self.loging_configuration_group_box.setFont(font)
        self.loging_configuration_group_box.setGeometry(QtCore.QRect(50, 40, 430, 140))
        self.loging_configuration_group_box.setObjectName("configuration_group_box")

        self.input_username = QtWidgets.QLineEdit(self.loging_configuration_group_box)
        self.input_username.setGeometry(QtCore.QRect(130, 30, 200, 20))
        self.input_username.setFont(font)
        self.input_username.textEdited.connect(self.__validate_input)
        self.input_username.setPlaceholderText(instagram.PLACEHOLDER_USERNAME)
        self.input_username.setObjectName("input_username")

        self.label_username = QtWidgets.QLabel(self.loging_configuration_group_box)
        self.label_username.setGeometry(QtCore.QRect(40, 30, 80, 20))
        self.label_username.setFont(font)
        self.label_username.setObjectName("label_username")

        self.input_password = QtWidgets.QLineEdit(self.loging_configuration_group_box)
        self.input_password.setGeometry(QtCore.QRect(130, 60, 200, 20))
        self.input_password.setFont(font)
        self.input_password.setObjectName("input_password")
        self.input_password.setPlaceholderText(instagram.PLACEHOLDER_PASSWORD)
        self.input_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.label_password = QtWidgets.QLabel(self.loging_configuration_group_box)
        self.label_password.setGeometry(QtCore.QRect(40, 60, 80, 20))
        self.label_password.setFont(font)
        self.label_password.setObjectName("label_password")

        self.input_profile = QtWidgets.QLineEdit(self.loging_configuration_group_box)
        self.input_profile.setGeometry(QtCore.QRect(130, 90, 200, 20))
        self.input_profile.setFont(font)
        self.input_profile.textEdited.connect(self.__validate_input)
        self.input_profile.setPlaceholderText(instagram.PLACEHOLDER_PROFILE_NAME)
        self.input_profile.setObjectName("input_profile")

        self.label_profile = QtWidgets.QLabel(self.loging_configuration_group_box)
        self.label_profile.setGeometry(QtCore.QRect(40, 90, 80, 20))
        self.label_profile.setFont(font)
        self.label_profile.setObjectName("label_profile")

        # Verify if input fields are empty
        self.input_fields = [
            self.input_username,
            self.input_password,
            self.input_profile,
        ]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        # ACQUISITION GROUP BOX
        self.acquisition_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.acquisition_group_box.setFont(font)
        self.acquisition_group_box.setEnabled(False)
        self.acquisition_group_box.setGeometry(QtCore.QRect(50, 200, 430, 180))
        self.acquisition_group_box.setObjectName("acquisition_group_box")

        # BASIC INFORMATION
        self.label_base_info = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_base_info.setGeometry(QtCore.QRect(20, 30, 111, 20))
        self.label_base_info.setFont(font)
        self.label_base_info.setObjectName("label_base_info")

        self.label_complete_name = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_complete_name.setGeometry(QtCore.QRect(20, 50, 111, 20))
        self.label_complete_name.setFont(font)
        self.label_complete_name.setObjectName("label_complete_name")

        self.label_biography = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_biography.setGeometry(QtCore.QRect(20, 70, 111, 20))
        self.label_biography.setFont(font)
        self.label_biography.setObjectName("label_biography")

        self.label_number_of_post = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_number_of_post.setGeometry(QtCore.QRect(20, 90, 111, 20))
        self.label_number_of_post.setFont(font)
        self.label_number_of_post.setObjectName("label_number_of_post")

        self.label_profile_image = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_profile_image.setGeometry(QtCore.QRect(20, 110, 111, 20))
        self.label_profile_image.setFont(font)
        self.label_profile_image.setObjectName("label_profile_image")

        self.label_account_type = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_account_type.setGeometry(QtCore.QRect(20, 130, 221, 20))
        self.label_account_type.setFont(font)
        self.label_account_type.setObjectName("label_account_type")

        # ADDITIONAL_INFORMATION
        self.label_aditional_information = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_aditional_information.setGeometry(QtCore.QRect(230, 30, 150, 20))
        self.label_aditional_information.setFont(font)
        self.label_aditional_information.setObjectName("label_aditional_information")

        self.checkbox_post = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_post.setGeometry(QtCore.QRect(230, 50, 70, 17))
        self.checkbox_post.setFont(font)
        self.checkbox_post.setObjectName("checkbox_post")

        self.checkbox_followee = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_followee.setGeometry(QtCore.QRect(230, 70, 90, 17))
        self.checkbox_followee.setFont(font)
        self.checkbox_followee.setObjectName("checkbox_followee")

        self.checkbox_story = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_story.setGeometry(QtCore.QRect(230, 90, 70, 17))
        self.checkbox_story.setFont(font)
        self.checkbox_story.setObjectName("checkbox_story")

        self.checkbox_follower = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_follower.setGeometry(QtCore.QRect(230, 110, 90, 17))
        self.checkbox_follower.setFont(font)
        self.checkbox_follower.setObjectName("checkbox_follower")

        self.checkbox_highlight = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_highlight.setGeometry(QtCore.QRect(230, 130, 111, 17))
        self.checkbox_highlight.setFont(font)
        self.checkbox_highlight.setObjectName("checkbox_highlight")

        self.checkbox_tagged_post = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_tagged_post.setGeometry(QtCore.QRect(320, 50, 100, 17))
        self.checkbox_tagged_post.setFont(font)
        self.checkbox_tagged_post.setObjectName("checkbox_tagged_post")

        self.checkbox_saved_post = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_saved_post.setGeometry(QtCore.QRect(320, 70, 100, 17))
        self.checkbox_saved_post.setFont(font)
        self.checkbox_saved_post.setObjectName("checkbox_saved_post")

        self.login_button = QtWidgets.QPushButton(self)
        self.login_button.setGeometry(QtCore.QRect(395, 165, 70, 25))
        self.login_button.setObjectName("loginButton")
        self.login_button.setFont(font)
        self.login_button.clicked.connect(self.__login)
        self.login_button.setEnabled(False)

        self.scrape_button = QtWidgets.QPushButton(self)
        self.scrape_button.setGeometry(QtCore.QRect(410, 410, 70, 25))
        self.scrape_button.setObjectName("scrapeButton")
        self.scrape_button.setFont(font)
        self.scrape_button.clicked.connect(self.__scrape)
        self.scrape_button.setEnabled(False)

        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(517, 340, 131, 23))
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setHidden(True)
        self.status.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.status)

        self.retranslateUi()

        # ACQUISITION
        self.is_acquisition_running = False
        self.acquisition = Acquisition(
            logger_acquisition, self.progress_bar, self.status, self
        )
        self.acquisition.post_acquisition.finished.connect(
            self.__are_post_acquisition_finished
        )

    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.loging_configuration_group_box.setTitle(instagram.LOGIN_CONFIGURATION)
        self.label_username.setText(instagram.LABEL_USERNAME)
        self.label_password.setText(instagram.LABEL_PASSWORD)
        self.label_profile.setText(instagram.PROFILE_NAME)
        self.acquisition_group_box.setTitle(instagram.ACQUISITON_SETTINGS)
        self.label_base_info.setText(
            "<strong>" + instagram.BASIC_INFORMATION + "</strong>"
        )
        self.label_complete_name.setText(instagram.FULL_NAME)
        self.label_biography.setText(instagram.BIO)
        self.label_number_of_post.setText(instagram.POST_NUMBER)
        self.label_profile_image.setText(instagram.PROFILE_PIC)
        self.label_account_type.setText(instagram.ACCOUNT_TYPE)
        self.label_aditional_information.setText(
            "<strong>" + instagram.ADDITIONAL_INFORMATION + "</strong>"
        )
        self.checkbox_post.setText(instagram.POST)
        self.checkbox_followee.setText(instagram.FOLLOWING)
        self.checkbox_highlight.setText(instagram.HIGHLIGHTS)
        self.checkbox_story.setText(instagram.STORIES)
        self.checkbox_tagged_post.setText(instagram.TAGGED)
        self.checkbox_saved_post.setText(instagram.SAVED)
        self.checkbox_follower.setText(instagram.FOLLOWERS)
        self.scrape_button.setText(general.BUTTON_SCRAPE)
        self.login_button.setText(general.BUTTON_LOGIN)

    def __validate_input(self, text):
        sender = self.sender()
        sender.setText(text.replace(" ", ""))

    def __init_worker(self, checkbox, acquisition_group_box):
        self.thread_worker = QtCore.QThread()
        self.worker = InstagramWorker(
            self.instagram_controller,
            self.methods_to_execute,
            checkbox,
            acquisition_group_box,
        )

        self.worker.moveToThread(self.thread_worker)
        self.thread_worker.started.connect(self.worker.run)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread_worker.quit)

        self.worker.scraped.connect(self.__hanlde_scraped)
        self.worker.progress.connect(self.__handle_progress)
        self.worker.error.connect(self.__handle_error)
        self.worker.logged_in.connect(self.__handle_logged_in)

        self.thread_worker.start()

    def __handle_error(self, e):
        self.spinner.stop()
        if self.loging_configuration_group_box.isEnabled() is False:
            self.loging_configuration_group_box.setEnabled(True)

        self.setEnabled(True)

        title = instagram.SERVER_ERROR
        msg = Error.GENERIC_ERROR
        details = e

        if isinstance(e, dict):
            title = e.get("title")
            msg = e.get("msg")
            details = e.get("details")

        error_dlg = ErrorView(
            QtWidgets.QMessageBox.Icon.Information, title, msg, str(details)
        )
        error_dlg.exec()

    def __handle_progress(self):
        self.acquisition.upadate_progress_bar()

    def __scrape(self):
        self.spinner.start()
        self.acquisition_group_box.setEnabled(False)
        self.thread_worker.quit()
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec()
        self.__start_scraped()

    def __login(self):
        if self.loging_configuration_group_box.isEnabled() is True:
            self.loging_configuration_group_box.setEnabled(False)

        # Login params
        self.username = self.input_username.text()
        self.password = self.input_password.text()
        self.profile = self.input_profile.text()
        center_x = self.x() + self.width / 2
        center_y = self.y() + self.height / 2
        self.spinner.set_position(center_x, center_y)
        self.spinner.start()
        self.setEnabled(False)

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec()

        checkbox = [
            self.checkbox_followee,
            self.checkbox_follower,
            self.checkbox_highlight,
            self.checkbox_post,
            self.checkbox_saved_post,
            self.checkbox_tagged_post,
            self.checkbox_story,
        ]

        self.__init_worker(checkbox, self.acquisition_group_box)
        self.instagram_controller.set_login_information(
            self.username, self.password, self.profile
        )

    def __handle_logged_in(self):
        self.spinner.stop()
        self.setEnabled(True)
        self.scrape_button.setEnabled(True)
        self.login_button.setEnabled(False)

    def __start_scraped(self):
        if self.acquisition_directory is None:
            self.acquisition_directory = (
                self.menu_bar.case_view.form.controller.create_acquisition_directory(
                    "instagram",
                    self.configuration_general.configuration["cases_folder_path"],
                    self.case_info["name"],
                    self.input_profile.text(),
                )
            )

        self.is_acquisition_running = True

        self.methods_to_execute = [
            (self.checkbox_post.isChecked(), self.instagram_controller.scrape_post),
            (
                self.checkbox_followee.isChecked(),
                self.instagram_controller.scrape_followees,
            ),
            (
                self.checkbox_highlight.isChecked(),
                self.instagram_controller.scrape_highlights,
            ),
            (self.checkbox_story.isChecked(), self.instagram_controller.scrape_stories),
            (
                self.checkbox_tagged_post.isChecked(),
                self.instagram_controller.scrape_tagged_posts,
            ),
            (
                self.checkbox_saved_post.isChecked(),
                self.instagram_controller.scrape_saved_posts,
            ),
            (
                self.checkbox_follower.isChecked(),
                self.instagram_controller.scrape_followers,
            ),
            (True, self.instagram_controller.scrape_profile_picture),
            (True, self.instagram_controller.scrape_info),
        ]

        internal_tasks = list(
            filter(lambda task: task[0] == True, self.methods_to_execute)
        )

        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(0)
        self.acquisition.start(
            [], self.acquisition_directory, self.case_info, len(internal_tasks)
        )

        self.status.showMessage(Logger.SCRAPING_INSTAGRAM.format(self.profile))
        self.acquisition.logger.info(Logger.LOGGED_IN.format(self.username))
        self.acquisition.logger.info(Logger.SCRAPING_INSTAGRAM.format(self.profile))
        self.acquisition.info.add_task(
            tasks.SCRAPING_INSTAGRAM, state.STARTED, status.PENDING
        )

        # Create acquisition folder
        self.profile_dir = os.path.join(
            self.acquisition_directory, self.input_profile.text()
        )
        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir)

        self.instagram_controller.set_dir(self.profile_dir)
        checkbox = [
            self.checkbox_followee,
            self.checkbox_follower,
            self.checkbox_highlight,
            self.checkbox_post,
            self.checkbox_saved_post,
            self.checkbox_tagged_post,
            self.checkbox_story,
        ]
        self.__init_worker(checkbox, self.acquisition_group_box)

    def __hanlde_scraped(self):
        row = self.acquisition.info.get_row(tasks.SCRAPING_INSTAGRAM)
        self.acquisition.info.update_task(row, state.COMPLETED, status.SUCCESS, "")

        self.instagram_controller.create_zip(self.profile_dir)

        self.__zip_and_remove(self.profile_dir)

        self.acquisition.stop([], "", 1)
        self.acquisition.log_end_message()
        self.spinner.stop()

        self.acquisition.post_acquisition.execute(
            self.acquisition_directory, self.case_info, "instagram"
        )

    def __are_post_acquisition_finished(self):
        self.acquisition.set_completed_progress_bar()

        self.progress_bar.setHidden(True)
        self.status.showMessage("")

        self.setEnabled(True)

        self.__show_finish_acquisition_dialog()

        self.acquisition_directory = None
        self.is_acquisition_running = False

    def __show_finish_acquisition_dialog(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(Logger.ACQUISITION_FINISHED)
        msg.setText(Details.ACQUISITION_FINISHED)
        msg.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No
        )

        return_value = msg.exec()
        if return_value == QtWidgets.QMessageBox.StandardButton.Yes:
            self.__open_acquisition_directory()

    def __zip_and_remove(self, mail_dir):
        shutil.make_archive(mail_dir, "zip", mail_dir)

        try:
            shutil.rmtree(mail_dir)
        except OSError as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                tasks.INSTAGRAM,
                Error.DELETE_PROJECT_FOLDER,
                "Error: %s - %s." % (e.filename, e.strerror),
            )

            error_dlg.exec()

    def __open_acquisition_directory(self):
        platform = get_platform()

        if platform == "win":
            os.startfile(self.acquisition_directory)
        elif platform == "osx":
            subprocess.call(["open", self.acquisition_directory])
        else:  # platform == 'lin' || platform == 'other'
            subprocess.call(["xdg-open", self.acquisition_directory])

    def __on_text_changed(self):
        all_field_filled = all(input_field.text() for input_field in self.input_fields)
        self.login_button.setEnabled(all_field_filled)

    def __back_to_wizard(self):
        if self.is_acquisition_running is False:
            self.deleteLater()
            self.wizard.reload_case_info()
            self.wizard.show()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
