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

import requests
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QLabel

from view.menu_bar import MenuBar as MenuBarView

from view.error import Error as ErrorView
from view.spinner import Spinner
from view.acquisition.acquisition import Acquisition

from controller.entire_website import EntireWebsite as EntireWebsiteController

from common.constants import (
    details as Details,
    logger as Logger,
    tasks,
    state,
    status,
    error as Error,
)
from common.constants.view import general, entire_site
from common.utility import get_platform

logger_acquisition = logging.getLogger(__name__)


class EntireWebsiteWorker(QtCore.QObject):
    scraped = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(object)
    valid_url = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(self, entire_website_controller, input_url):
        super().__init__()
        self.entire_website_controller = entire_website_controller
        self.input_url = input_url

    @QtCore.pyqtSlot()
    def run(self):
        # todo
        self.finished.emit()


class EntireWebsite(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(EntireWebsite, self).__init__(*args, **kwargs)
        self.acquisition_directory = None
        self.acquisition_is_started = False
        self.is_enabled_timestamp = False
        self.spinner = Spinner()
        self.entire_website_controller = EntireWebsiteController()

    def init(self, case_info, wizard, options=None):
        self.__init__()
        self.wizard = wizard
        self.case_info = case_info

        self.setWindowIcon(QtGui.QIcon(os.path.join("assets/svg/", "FIT.svg")))

        # set font
        font = QtGui.QFont()
        font.setPointSize(10)

        self.setObjectName("mainWindow")
        self.width = 990
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

        # URL CONFIGURATION GROUP BOX
        self.url_configuration_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.url_configuration_group_box.setEnabled(True)
        self.url_configuration_group_box.setFont(font)
        self.url_configuration_group_box.setGeometry(QtCore.QRect(50, 20, 430, 200))
        self.url_configuration_group_box.setObjectName("configuration_group_box")

        self.label_url = QtWidgets.QLabel(self.url_configuration_group_box)
        self.label_url.setGeometry(QtCore.QRect(20, 80, 80, 20))
        self.label_url.setFont(font)
        self.label_url.setObjectName("label_url")

        self.input_url = QtWidgets.QLineEdit(self.url_configuration_group_box)
        self.input_url.setGeometry(QtCore.QRect(100, 80, 290, 20))
        self.input_url.setFont(font)
        self.input_url.setObjectName("input_url")
        self.input_url.setPlaceholderText(entire_site.PLACEHOLDER_URL)

        # Verify if input fields are empty
        self.input_fields = [self.input_url]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        # ACQUISITION GROUP BOX
        self.acquisition_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.acquisition_group_box.setFont(font)
        self.acquisition_group_box.setEnabled(False)
        self.acquisition_group_box.setGeometry(QtCore.QRect(50, 240, 430, 140))
        self.acquisition_group_box.setObjectName("acquisition_group_box")

        # LOAD BUTTON
        self.load_button = QtWidgets.QPushButton(self)
        self.load_button.setGeometry(QtCore.QRect(400, 410, 80, 25))
        self.load_button.setObjectName("loadButton")
        self.load_button.setFont(font)
        self.load_button.clicked.connect(self.__load)
        self.load_button.setEnabled(False)

        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(517, 340, 131, 23))
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setHidden(True)
        self.status.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.status)

        # URL PREVIEW GROUP BOX
        self.url_preview_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.url_preview_group_box.setEnabled(True)
        self.url_preview_group_box.setFont(font)
        self.url_preview_group_box.setGeometry(QtCore.QRect(515, 20, 430, 360))
        self.url_preview_group_box.setObjectName("url_preview_group_box")

        # SCRAPE BUTTON
        self.scrape_button = QtWidgets.QPushButton(self)
        self.scrape_button.setGeometry(QtCore.QRect(875, 410, 70, 25))
        self.scrape_button.setObjectName("scrapeButton")
        self.scrape_button.setFont(font)
        self.scrape_button.clicked.connect(self.__scrape)
        self.scrape_button.setEnabled(False)

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
        self.url_configuration_group_box.setTitle(entire_site.URL_CONFIGURATION)
        self.url_preview_group_box.setTitle(entire_site.CRAWLED_URLS)
        self.label_url.setText(entire_site.URL)
        self.scrape_button.setText(general.DOWNLOAD)

        self.load_button.setText(general.BUTTON_LOAD)
        self.scrape_button.setText(general.DOWNLOAD)

    def __init_worker(self):
        self.thread_worker = QtCore.QThread()
        self.worker = EntireWebsiteWorker(
            self.entire_website_controller, self.input_url
        )

        self.worker.moveToThread(self.thread_worker)
        self.thread_worker.started.connect(self.worker.run)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread_worker.quit)

        self.worker.scraped.connect(self.__hanlde_scraped)
        self.worker.progress.connect(self.__handle_progress)
        self.worker.error.connect(self.__handle_error)
        self.worker.valid_url.connect(self.__handle_valid_url)

        self.thread_worker.start()

    def __handle_error(self, e):
        self.spinner.stop()
        if self.url_configuration_group_box.isEnabled() is False:
            self.url_configuration_group_box.setEnabled(True)

        self.setEnabled(True)

        title = entire_site.SERVER_ERROR
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

    def __load(self):
        # video_url
        self.url = self.input_url.text()
        center_x = self.x() + self.width / 2
        center_y = self.y() + self.height / 2
        self.spinner.set_position(center_x, center_y)
        self.spinner.start()

        self.setEnabled(False)

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec()
        if self.entire_website_controller.url is None:
            self.__init_worker()
            self.acquisition_group_box.setEnabled(True)
        else:
            self.acquisition_group_box.setEnabled(True)
            self.__start_scraped()

    def __scrape(self):

        self.url = self.input_url.text()
        center_x = self.x() + self.width / 2
        center_y = self.y() + self.height / 2
        self.spinner.set_position(center_x, center_y)
        self.spinner.start()
        self.setEnabled(False)

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec()
        if self.entire_website_controller.url is None:
            self.__init_worker()
        else:
            self.__start_scraped()

    def __handle_valid_url(self):
        self.thread_worker.quit()
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec()

        self.__load_info()

    def __load_info(self):
        self.setEnabled(True)
        self.status.showMessage("")
        # todo crawler

        self.spinner.stop()
        self.is_acquisition_running = False

    def __start_scraped(self):
        if self.acquisition_directory is None:
            self.acquisition_directory = (
                self.menu_bar.case_view.form.controller.create_acquisition_directory(
                    "entire_website",
                    self.configuration_general.configuration["cases_folder_path"],
                    self.case_info["name"],
                    self.input_url.text(),
                )
            )

        self.is_acquisition_running = True

        internal_tasks = list()

        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(0)
        self.acquisition.start(
            [], self.acquisition_directory, self.case_info, len(internal_tasks)
        )

        self.status.showMessage(Logger.DOWNLOAD_VIDEO)
        self.acquisition.logger.info(Logger.DOWNLOAD_VIDEO)
        self.acquisition.info.add_task(
            tasks.DOWNLOAD_VIDEO, state.STARTED, status.PENDING
        )
        self.entire_website_controller.set_id()

        self.url_dir = os.path.join(
            self.acquisition_directory, self.entire_website_controller.id_digest
        )
        if not os.path.exists(self.url_dir):
            os.makedirs(self.url_dir)

        self.__init_worker()

    def __hanlde_scraped(self):
        row = self.acquisition.info.get_row(tasks.CRAWL)
        self.acquisition.info.update_task(row, state.FINISHED, status.COMPLETED, "")

        self.entire_website_controller.create_zip(self.url_dir)

        self.__zip_and_remove(self.url_dir)

        self.acquisition.stop([], "", 1)
        self.acquisition.log_end_message()
        self.spinner.stop()

        self.acquisition.post_acquisition.execute(
            self.acquisition_directory, self.case_info, "entire_website"
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

    def __zip_and_remove(self, video_dir):
        shutil.make_archive(video_dir, "zip", video_dir)

        try:
            shutil.rmtree(video_dir)
        except OSError as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                tasks.DOWNLOAD_VIDEO,
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
        self.load_button.setEnabled(all_field_filled)

    def __back_to_wizard(self):
        if self.is_acquisition_running is False:
            self.deleteLater()
            self.wizard.reload_case_info()
            self.wizard.show()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
