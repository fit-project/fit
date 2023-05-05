# !/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
#
# Copyright (c) 2022 FIT-Project and others
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
######
import os
import shutil

import zipfile

from PyQt5 import QtCore, QtGui, QtWidgets
from instaloader import InvalidArgumentException, BadCredentialsException, ConnectionException, \
    ProfileNotExistsException

from common.constants.view import general, instagram
from controller.instagram import Instagram as InstragramController
from view.error import Error as ErrorView

from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView

from common.config import LogConfigTools
from common.constants import tasks, state, status, error as Error

from common.constants import details as Details, logger as Logger

import logging.config
from view.acquisition.acquisition import Acquisition

logger_acquisition = logging.getLogger(__name__)


class Instagram(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Instagram, self).__init__(*args, **kwargs)
        self.acquisition_directory = None
        self.acquisition_is_started = False
        self.is_enabled_timestamp = False

    def init(self, case_info, wizard, options=None):
        self.__init__()
        self.wizard = wizard
        self.case_info = case_info
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()
        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()
        self.log_confing = LogConfigTools()

        self.setObjectName("mainWindow")
        self.resize(653, 392)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # MENU BAR
        self.setCentralWidget(self.centralwidget)
        self.menuBar().setNativeMenuBar(False)

        # CONF BUTTON
        self.menu_configuration = QtWidgets.QAction("Configuration", self)
        self.menu_configuration.setObjectName("menu_configuration")
        self.menu_configuration.triggered.connect(self.__configuration)
        self.menuBar().addAction(self.menu_configuration)

        # CASE BUTTON
        self.case_action = QtWidgets.QAction("Case", self)
        self.case_action.setStatusTip("Show case info")
        self.case_action.triggered.connect(self.__case)
        self.menuBar().addAction(self.case_action)

        # BACK TO WIZARD
        back_action = QtWidgets.QAction("Back to wizard", self)
        back_action.setStatusTip("Go back to the main menu")
        back_action.triggered.connect(self.__back_to_wizard)
        self.menuBar().addAction(back_action)

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")

        # Get timestamp parameters
        self.configuration_timestamp = self.configuration_view.get_tab_from_name("configuration_timestamp")

        self.input_username = QtWidgets.QLineEdit(self.centralwidget)
        self.input_username.setGeometry(QtCore.QRect(240, 30, 240, 20))
        self.input_username.setObjectName("input_username")

        self.input_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_password.setGeometry(QtCore.QRect(240, 60, 240, 20))
        self.input_password.setObjectName("input_password")
        self.input_password.setEchoMode(QtWidgets.QLineEdit.Password)

        self.label_username = QtWidgets.QLabel(self.centralwidget)
        self.label_username.setGeometry(QtCore.QRect(80, 30, 100, 20))
        self.label_username.setObjectName("label_username")

        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QtCore.QRect(80, 60, 100, 20))
        self.label_password.setObjectName("label_password")

        self.scrapeButton = QtWidgets.QPushButton(self.centralwidget)
        self.scrapeButton.setGeometry(QtCore.QRect(520, 270, 75, 25))
        self.scrapeButton.setObjectName("scrapeButton")
        self.scrapeButton.clicked.connect(self.__save_profile)
        self.scrapeButton.setEnabled(False)

        self.input_profile = QtWidgets.QLineEdit(self.centralwidget)
        self.input_profile.setGeometry(QtCore.QRect(240, 90, 240, 20))
        self.input_profile.setText("")
        self.input_profile.setObjectName("input_profile")

        # Verify if input fields are empty
        self.input_fields = [self.input_username, self.input_password, self.input_profile]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        self.label_profile = QtWidgets.QLabel(self.centralwidget)
        self.label_profile.setGeometry(QtCore.QRect(80, 90, 141, 20))
        self.label_profile.setObjectName("label_profile")
        self.label_baseInfo = QtWidgets.QLabel(self.centralwidget)
        self.label_baseInfo.setGeometry(QtCore.QRect(80, 140, 111, 20))
        self.label_baseInfo.setObjectName("label_baseInfo")

        self.checkBox_post = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_post.setGeometry(QtCore.QRect(360, 170, 70, 17))
        self.checkBox_post.setObjectName("checkBox_post")

        self.checkBox_2_followee = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2_followee.setGeometry(QtCore.QRect(360, 190, 70, 17))
        self.checkBox_2_followee.setObjectName("checkBox_2_followee")

        self.checkBox_3_highlight = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3_highlight.setGeometry(QtCore.QRect(430, 190, 111, 17))
        self.checkBox_3_highlight.setObjectName("checkBox_3_highlight")

        self.checkBox_4_story = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_4_story.setGeometry(QtCore.QRect(360, 230, 70, 17))
        self.checkBox_4_story.setObjectName("checkBox_4_story")

        self.checkBox_5_taggedPost = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_5_taggedPost.setGeometry(QtCore.QRect(430, 210, 91, 17))
        self.checkBox_5_taggedPost.setObjectName("checkBox_5_taggedPost")

        self.checkBox_6_savedPost = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_6_savedPost.setGeometry(QtCore.QRect(430, 170, 91, 17))
        self.checkBox_6_savedPost.setObjectName("checkBox_6_savedPost")

        self.checkBox_7_follower = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_7_follower.setGeometry(QtCore.QRect(360, 210, 70, 17))
        self.checkBox_7_follower.setObjectName("checkBox_7_follower")

        self.label_optionalInfo = QtWidgets.QLabel(self.centralwidget)
        self.label_optionalInfo.setGeometry(QtCore.QRect(360, 140, 121, 20))
        self.label_optionalInfo.setObjectName("label_optionalInfo")

        self.label_completeName = QtWidgets.QLabel(self.centralwidget)
        self.label_completeName.setGeometry(QtCore.QRect(80, 170, 111, 20))
        self.label_completeName.setObjectName("label_completeName")

        self.label_biography = QtWidgets.QLabel(self.centralwidget)
        self.label_biography.setGeometry(QtCore.QRect(80, 190, 111, 20))
        self.label_biography.setObjectName("label_biography")

        self.label_numberOfPost = QtWidgets.QLabel(self.centralwidget)
        self.label_numberOfPost.setGeometry(QtCore.QRect(80, 210, 111, 20))
        self.label_numberOfPost.setObjectName("label_numberOfPost")

        self.label_profileImage = QtWidgets.QLabel(self.centralwidget)
        self.label_profileImage.setGeometry(QtCore.QRect(80, 230, 111, 20))
        self.label_profileImage.setObjectName("label_profileImage")

        self.label_accountType = QtWidgets.QLabel(self.centralwidget)
        self.label_accountType.setGeometry(QtCore.QRect(80, 250, 221, 20))
        self.label_accountType.setObjectName("label_accountType")

        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(517, 340, 131, 23))
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setHidden(True)
        self.status.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.status)
        self.configuration_network = self.configuration_general.findChild(QtWidgets.QGroupBox,
                                                                          'group_box_network_check')

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowIcon(QtGui.QIcon(os.path.join('assets/svg/', 'FIT.svg')))

        # ACQUISITION
        self.acquisition_is_running = False
        self.acquisition = Acquisition(logger_acquisition, self.progress_bar, self.status, self)

    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.label_username.setText(instagram.LABEL_USERNAME)
        self.label_password.setText(instagram.LABEL_PASSWORD)
        self.scrapeButton.setText(instagram.SCRAPE_BUTTON)
        self.label_profile.setText(instagram.PROFILE_NAME)
        self.label_baseInfo.setText(instagram.BASIC_INFORMATION)
        self.checkBox_post.setText(instagram.POST)
        self.checkBox_2_followee.setText(instagram.FOLLOWING)
        self.checkBox_3_highlight.setText(instagram.HIGHLIGHTS)
        self.checkBox_4_story.setText(instagram.STORIES)
        self.checkBox_5_taggedPost.setText(instagram.TAGGED)
        self.checkBox_6_savedPost.setText(instagram.SAVED)
        self.checkBox_7_follower.setText(instagram.FOLLOWERS)
        self.label_optionalInfo.setText(instagram.ADDITIONAL)
        self.label_completeName.setText(instagram.FULL_NAME)
        self.label_biography.setText(instagram.BIO)
        self.label_numberOfPost.setText(instagram.POST_NUMBER)
        self.label_profileImage.setText(instagram.PROFILE_PIC)
        self.label_accountType.setText(instagram.VERIFIED)

    def __save_profile(self):

        insta = InstragramController(self.input_username.text(), self.input_password.text(),
                                     self.input_profile.text())
        try:
            insta.login()
        except (InvalidArgumentException, BadCredentialsException, ConnectionException, ProfileNotExistsException) as e:
            error_message = str(e)
            error_title = ""
            error_type = ""
            if isinstance(e, InvalidArgumentException):
                error_title = instagram.INVALID_USER
                error_type = Error.INVALID_USER
            elif isinstance(e, BadCredentialsException):
                error_title = instagram.LOGIN_ERROR
                error_type = Error.PASSWORD_ERROR
            elif isinstance(e, ConnectionException):
                error_title = instagram.CONNECTION_ERROR
                error_type = Error.LOGIN_ERROR
            elif isinstance(e, ProfileNotExistsException):
                error_title = instagram.INVALID_PROFILE
                error_type = Error.INVALID_PROFILE

            error_dlg = ErrorView(QtWidgets.QMessageBox.Information, error_title, error_type, error_message)
            error_dlg.exec_()
        else:
            # Create acquisition directory
            self.acquisition_directory = self.case_view.form.controller.create_acquisition_directory(
                'instagram',
                self.configuration_general.configuration['cases_folder_path'],
                self.case_info['name'],
                self.input_profile.text()
            )
            self.acquisition_is_running = True
            if self.acquisition_directory is not None:
                # show progress bar
                self.progress_bar.setHidden(False)
                self.acquisition.start([], self.acquisition_directory, self.case_info, 1)

            self.status.showMessage(Logger.FETCH_PROFILE)
            self.acquisition.logger.info(Logger.FETCH_PROFILE)
            self.acquisition.info.add_task(tasks.FETCH_PROFILE, state.STARTED, status.PENDING)
            # Create acquisition folder
            self.profile_dir = os.path.join(self.acquisition_directory, self.input_profile.text())
            if not os.path.exists(self.profile_dir):
                os.makedirs(self.profile_dir)

            insta.set_dir(self.profile_dir)

            row = self.acquisition.info.get_row(tasks.FETCH_PROFILE)
            self.acquisition.info.update_task(row, state.FINISHED, status.COMPLETED, '')
            self.acquisition.upadate_progress_bar()

            self.status.showMessage(Logger.SCRAPING_INSTAGRAM)
            self.acquisition.logger.info(Logger.SCRAPING_INSTAGRAM)
            self.acquisition.info.add_task(tasks.SCRAPING_INSTAGRAM, state.STARTED, status.PENDING)

            self.setEnabled(False)

            methods_to_execute = [
                (self.checkBox_post.isChecked, insta.scrape_post),
                (self.checkBox_2_followee.isChecked, insta.scrape_followees),
                (self.checkBox_3_highlight.isChecked, insta.scrape_highlights),
                (self.checkBox_4_story.isChecked, insta.scrape_stories),
                (self.checkBox_5_taggedPost.isChecked, insta.scrape_tagged_posts),
                (self.checkBox_6_savedPost.isChecked, insta.scrape_saved_posts),
                (self.checkBox_7_follower.isChecked, insta.scrape_followers)
            ]

            for checkbox, method in methods_to_execute:
                if checkbox():
                    method()
            insta.scrape_profile_picture()
            insta.scrape_info()

            self.__zip_and_remove(self.profile_dir)

            row = self.acquisition.info.get_row(tasks.SCRAPING_INSTAGRAM)
            self.acquisition.info.update_task(row, state.FINISHED, status.COMPLETED, '')
            self.acquisition.upadate_progress_bar()

            self.acquisition.stop([], '', 1)
            self.acquisition.log_end_message()

            self.acquisition.post_acquisition.execute(self.acquisition_directory, self.case_info, 'instagram')
            self.setEnabled(True)
            self.acquisition_is_running = False
            self.__show_finish_acquisition_dialog()

    def __show_finish_acquisition_dialog(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(Logger.ACQUISITION_FINISHED)
        msg.setText(Details.ACQUISITION_FINISHED)
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        return_value = msg.exec()
        if return_value == QtWidgets.QMessageBox.Yes:
            self.__open_acquisition_directory()

    def __zip_and_remove(self, mail_dir):

        shutil.make_archive(mail_dir, 'zip', mail_dir)

        try:
            shutil.rmtree(mail_dir)
        except OSError as e:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                                  tasks.INSTAGRAM,
                                  Error.DELETE_PROJECT_FOLDER,
                                  "Error: %s - %s." % (e.filename, e.strerror)
                                  )

            error_dlg.buttonClicked.connect(quit)

    def __open_acquisition_directory(self):
        os.startfile(self.acquisition_directory)

    def __on_text_changed(self):
        all_field_filled = all(input_field.text() for input_field in self.input_fields)
        self.scrapeButton.setEnabled(all_field_filled)

    def __case(self):
        self.case_view.exec_()

    def __configuration(self):
        self.configuration_view.exec_()

    def __back_to_wizard(self):
        if self.acquisition_is_running is False:
            self.deleteLater()
            self.wizard.reload_case_info()
            self.wizard.show()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
