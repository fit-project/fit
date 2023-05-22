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
import shutil

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import (QObject, QThread, QRect, QMetaObject,
                          pyqtSignal, QEventLoop, QTimer, pyqtSlot)
from PyQt6.QtGui import QFont, QIcon
from PyQt6 import QtCore

from view.acquisition.acquisition import Acquisition
from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView
from view.error import Error as ErrorView
from view.spinner import Spinner

from controller.youtube import Youtube as YoutubeController

from common.constants.view import mail, general, youtube
from common.constants.view.pec import search_pec

from common.constants import tasks, error, details as Details, logger as Logger

logger_acquisition = logging.getLogger(__name__)


class YoutubeWorker(QObject):
    download = pyqtSignal()
    progress = pyqtSignal()
    error = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, youtube_controller, url, acquisition_directory, is_downloading):
        super().__init__()
        self.youtube_controller = youtube_controller
        self.url = url
        self.acquisition_directory = acquisition_directory
        self.is_downloading = is_downloading

    @pyqtSlot()
    def run(self):
        try:
            self.__download_video()

        except Exception as e:
            self.error.emit(e)
        else:
            self.download.emit()
        finally:
            self.finished.emit()

    def __download_video(self):
        self.youtube_controller.download_video(self.url, self.acquisition_directory)
        self.progress.emit()


class Youtube(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Youtube, self).__init__(*args, **kwargs)
        self.url = None
        self.increment = 0
        self.youtube_controller = YoutubeController()
        self.spinner = Spinner()
        self.acquisition_directory = None
        self.case_info = None
        self.configuration_view = ConfigurationView(self)

    def init(self, case_info, wizard, options=None):

        self.__init__()
        self.wizard = wizard
        self.width = 600
        self.height = 230
        self.setFixedSize(self.width, self.height)
        self.case_info = case_info
        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()
        self.setWindowIcon(QtGui.QIcon(os.path.join('assets/svg/', 'FIT.svg')))
        self.setObjectName("verify_pec_window")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("QWidget {background-color: rgb(255, 255, 255);}")
        self.setCentralWidget(self.centralwidget)

        # MENU BAR
        self.setCentralWidget(self.centralwidget)
        self.menuBar().setNativeMenuBar(False)

        # CONF BUTTON
        self.menu_configuration = QtGui.QAction('Configuration', self)
        self.menu_configuration.setObjectName("menuConfiguration")
        self.menu_configuration.triggered.connect(self.__configuration)
        self.menuBar().addAction(self.menu_configuration)

        # CASE BUTTON
        self.case_action = QtGui.QAction('Case', self)
        self.case_action.setStatusTip("Show case info")
        self.case_action.triggered.connect(self.__case)
        self.menuBar().addAction(self.case_action)

        # set font
        font = QFont()
        font.setPointSize(10)

        # PROGRESS BAR
        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximumWidth(400)
        self.progress_bar.setFixedHeight(25)
        self.status.addPermanentWidget(self.progress_bar)

        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setStatusBar(self.status)
        self.progress_bar.setHidden(True)

        self.url_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.url_group_box.setEnabled(True)
        self.url_group_box.setGeometry(QtCore.QRect(50, 20, 500, 140))
        self.url_group_box.setObjectName("url_group_box")

        # URL
        self.input_url = QtWidgets.QLineEdit(self.centralwidget)
        self.input_url.setGeometry(QtCore.QRect(160, 60, 260, 20))
        self.input_url.setObjectName("input_url")
        self.input_url.setEnabled(True)

        # URL LABEL
        self.label_url = QtWidgets.QLabel(self.centralwidget)
        self.label_url.setGeometry(QtCore.QRect(90, 60, 60, 20))
        self.label_url.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.label_url.setObjectName("label_url")

        # DOWNLOAD BUTTON
        self.download_button = QtWidgets.QPushButton(self.centralwidget)
        self.download_button.setGeometry(QtCore.QRect(450, 100, 75, 30))
        self.download_button.clicked.connect(self.__download)
        self.download_button.setObjectName("StartAction")
        self.download_button.setEnabled(False)

        # DISABLE SCRAPE BUTTON IF FIELDS ARE EMPTY
        self.input_fields = [self.input_url]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")

        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)

        self.setWindowIcon(QIcon(os.path.join('assets/svg/', 'FIT.svg')))

        # ACQUISITION
        self.acquisition = Acquisition(logger_acquisition, self.progress_bar, self.status, self)
        self.acquisition.post_acquisition.finished.connect(self.__are_post_acquisition_finished)
        self.is_first_acquisition_completed = False
        self.is_acquisition_running = False


    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.url_group_box.setTitle(youtube.SETTINGS)
        self.label_url.setText(youtube.INPUT_URL)
        self.download_button.setText(youtube.DOWNLOAD)

    def __init_worker(self):
        self.thread_worker = QThread()
        self.worker = YoutubeWorker(self.youtube_controller, self.url, self.acquisition_youtube_dir, self.is_downloading)

        self.worker.moveToThread(self.thread_worker)
        self.thread_worker.started.connect(self.worker.run)

        self.worker.finished.connect(self.thread_worker.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread_worker.finished.connect(self.thread_worker.deleteLater)

        self.worker.download.connect(self.__handle_download)

        self.worker.progress.connect(self.__handle_progress)
        self.worker.error.connect(self.__handle_error)

        self.thread_worker.start()

    def __handle_error(self, e):

        self.spinner.stop()
        if self.configuration_group_box.isEnabled() is False:
            self.configuration_group_box.setEnabled(True)
        self.setEnabled(True)

        title = youtube.SERVER_ERROR
        msg = error.YOUTUBE_SERVER_ERROR
        details = e

        if isinstance(e, dict):
            title = e.get('title')
            msg = e.get('msg')
            details = e.get('details')

        error_dlg = ErrorView(QtWidgets.QMessageBox.Icon.Information,
                              title,
                              msg,
                              str(details))
        error_dlg.exec()


    def __start(self):

        if self.acquisition_directory is None:
            # Create acquisition directory
            self.acquisition_directory = self.case_view.form.controller.create_acquisition_directory(
                'youtube',
                self.configuration_general.configuration['cases_folder_path'],
                self.case_info['name'],
                self.input_url.text()
            )

        if self.acquisition_directory is not None:
            if self.is_acquisition_running is False:
                self.is_acquisition_running = True
                self.acquisition.start([], self.acquisition_directory, self.case_info, 1)

    def __on_text_changed(self, text):

        all_fields_filled = all(input_field.text() for input_field in self.input_fields)
        self.download_button.setEnabled(all_fields_filled)

    def __download(self):
        self.is_acquisition_running = True
        self.is_downloading = True
        self.setEnabled(False)
        self.url = self.input_url.text()
        self.__start()

        self.status.showMessage(Logger.DOWNLOAD_VIDEO)
        self.acquisition.logger.info(Logger.DOWNLOAD_VIDEO)

        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(0)

        self.spinner.start()
        self.setEnabled(False)

        # wait for 1 second
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec()

        # Create acquisition folder
        self.acquisition_youtube_dir = os.path.join(self.acquisition_directory, 'acquisition_youtube')
        if not os.path.exists(self.acquisition_youtube_dir):
            os.makedirs(self.acquisition_youtube_dir)

        self.increment = 100
        self.__init_worker()

    def __handle_download(self):
        self.is_downloading = False
        self.__zip_and_remove(self.acquisition_youtube_dir)
        self.acquisition.set_completed_progress_bar()

        self.acquisition.stop([], '', 1)
        self.acquisition.log_end_message()
        self.spinner.stop()

        self.acquisition.post_acquisition.execute(self.acquisition_directory, self.case_info, 'youtube')

    def __are_post_acquisition_finished(self):
        self.setEnabled(True)

        self.progress_bar.setHidden(True)
        self.status.showMessage('')

        self.__show_finish_acquisition_dialog()

        self.acquisition_directory = None
        self.is_acquisition_running = False

    def __handle_progress(self):
        self.acquisition.upadate_progress_bar()

    def __zip_and_remove(self, mail_dir):

        shutil.make_archive(mail_dir, 'zip', mail_dir)

        try:
            shutil.rmtree(mail_dir)
        except OSError as e:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Icon.Critical,
                                  tasks.YOUTUBE,
                                  error.DELETE_PROJECT_FOLDER,
                                  "Error: %s - %s." % (e.filename, e.strerror)
                                  )

            error_dlg.exec()

    def __show_finish_acquisition_dialog(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(Logger.ACQUISITION_FINISHED)
        msg.setText(Details.ACQUISITION_FINISHED)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)

        return_value = msg.exec()
        if return_value == QtWidgets.QMessageBox.StandardButton.Yes:
            self.__open_acquisition_directory()

    def __open_acquisition_directory(self):
        os.startfile(self.acquisition_directory)

    def __case(self):
        self.case_view.exec()

    def __configuration(self):
        self.configuration_view.exec()

    def __back_to_wizard(self):
        if self.is_acquisition_running is False:
            self.deleteLater()
            self.wizard.reload_case_info()
            self.wizard.show()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
