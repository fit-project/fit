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

from PyQt6 import QtCore, QtGui, QtWidgets

from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView
from view.error import Error as ErrorView
from view.spinner import Spinner
from view.acquisition.acquisition import Acquisition

from controller.video import Video as VideoController
from common.constants import details as Details, logger as Logger, tasks, state, status, error as Error
from common.constants.view import general, mail, video

logger_acquisition = logging.getLogger(__name__)


class VideoWorker(QtCore.QObject):
    scraped = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(object)
    finished = QtCore.pyqtSignal()

    def __init__(self, video_controller, methods_to_execute):
        super().__init__()
        self.video_controller = video_controller
        self.methods_to_execute = methods_to_execute

    @QtCore.pyqtSlot()
    def run(self):
        for checkbox, method in self.methods_to_execute:
            if checkbox:
                method()
                self.progress.emit()

        self.scraped.emit()
        self.finished.emit()


class Video(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Video, self).__init__(*args, **kwargs)
        self.acquisition_directory = None
        self.acquisition_is_started = False
        self.is_enabled_timestamp = False
        self.methods_to_execute = None
        self.spinner = Spinner()
        self.video_controller = VideoController()

    def init(self, case_info, wizard, options=None):
        self.__init__()
        self.wizard = wizard
        self.case_info = case_info
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()
        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()

        self.setWindowIcon(QtGui.QIcon(os.path.join('assets/svg/', 'FIT.svg')))

        # set font
        font = QtGui.QFont()
        font.setPointSize(10)

        self.setObjectName("mainWindow")
        self.resize(530, 480)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setStyleSheet("QWidget {background-color: rgb(255, 255, 255);}")
        self.centralwidget.setObjectName("centralwidget")

        # MENU BAR
        self.setCentralWidget(self.centralwidget)
        self.menuBar().setNativeMenuBar(False)

        # CONF BUTTON
        self.menu_configuration = QtGui.QAction('Configuration', self)
        self.menu_configuration.setObjectName("menu_configuration")
        self.menu_configuration.triggered.connect(self.__configuration)
        self.menuBar().addAction(self.menu_configuration)

        # CASE BUTTON
        self.case_action = QtGui.QAction('Case', self)
        self.case_action.setStatusTip("Show case info")
        self.case_action.triggered.connect(self.__case)
        self.menuBar().addAction(self.case_action)

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")

        # Get timestamp parameters
        self.configuration_timestamp = self.configuration_view.get_tab_from_name("configuration_timestamp")

        # LOGIN CONFIGURATION GROUP BOX
        self.url_configuration_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.url_configuration_group_box.setEnabled(True)
        self.url_configuration_group_box.setFont(font)
        self.url_configuration_group_box.setGeometry(QtCore.QRect(50, 40, 430, 140))
        self.url_configuration_group_box.setObjectName("configuration_group_box")


        self.input_url = QtWidgets.QLineEdit(self.url_configuration_group_box)
        self.input_url.setGeometry(QtCore.QRect(130, 60, 240, 20))
        self.input_url.setFont(font)
        self.input_url.setObjectName("input_url")
        self.input_url.setPlaceholderText(video.PLACEHOLDER_URL)

        self.label_url = QtWidgets.QLabel(self.url_configuration_group_box)
        self.label_url.setGeometry(QtCore.QRect(40, 60, 80, 20))
        self.label_url.setFont(font)
        self.label_url.setObjectName("label_url")


        # Verify if input fields are empty
        self.input_fields = [self.input_url]
        for input_field in self.input_fields:
            input_field.textChanged.connect(self.__on_text_changed)

        # ACQUISITION GROUP BOX
        self.acquisition_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.acquisition_group_box.setFont(font)
        self.acquisition_group_box.setEnabled(True)
        self.acquisition_group_box.setGeometry(QtCore.QRect(50, 200, 430, 180))
        self.acquisition_group_box.setObjectName("acquisition_group_box")

        # BASIC INFORMATION
        self.label_base_info = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_base_info.setGeometry(QtCore.QRect(20, 30, 111, 20))
        self.label_base_info.setFont(font)
        self.label_base_info.setObjectName("label_base_info")

        self.label_info = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_info.setGeometry(QtCore.QRect(20, 50, 111, 20))
        self.label_info.setFont(font)
        self.label_info.setObjectName("label_info")

        # ADDITIONAL_INFORMATION
        self.label_aditional_information = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_aditional_information.setGeometry(QtCore.QRect(230, 30, 150, 20))
        self.label_aditional_information.setFont(font)
        self.label_aditional_information.setObjectName("label_aditional_information")

        self.checkbox_audio = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_audio.setGeometry(QtCore.QRect(230, 50, 70, 17))
        self.checkbox_audio.setFont(font)
        self.checkbox_audio.setObjectName("checkbox_audio")


        self.scrape_button = QtWidgets.QPushButton(self.centralwidget)
        self.scrape_button.setGeometry(QtCore.QRect(410, 390, 70, 25))
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
        self.acquisition = Acquisition(logger_acquisition, self.progress_bar, self.status, self)
        self.acquisition.post_acquisition.finished.connect(self.__are_post_acquisition_finished)

    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.url_configuration_group_box.setTitle(video.URL_CONFIGURATION)

        self.label_url.setText(video.URL)

        self.acquisition_group_box.setTitle(video.ACQUISITON_SETTINGS)
        self.label_base_info.setText('<strong>' + video.BASIC_INFORMATION + '</strong>')
        self.label_info.setText(video.INFO)
        self.label_aditional_information.setText('<strong>' + video.ADDITIONAL_INFORMATION + '</strong>')
        self.checkbox_audio.setText(video.AUDIO)
        self.scrape_button.setText(general.BUTTON_SCRAPE)

    def __init_worker(self):
        self.thread_worker = QtCore.QThread()
        self.worker = VideoWorker(self.video_controller, self.methods_to_execute)

        self.worker.moveToThread(self.thread_worker)
        self.thread_worker.started.connect(self.worker.run)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread_worker.quit)

        self.worker.scraped.connect(self.__hanlde_scraped)
        self.worker.progress.connect(self.__handle_progress)
        self.worker.error.connect(self.__handle_error)

        self.thread_worker.start()

    def __handle_error(self, e):

        self.spinner.stop()
        if self.url_configuration_group_box.isEnabled() is False:
            self.url_configuration_group_box.setEnabled(True)

        self.setEnabled(True)

        title = mail.SERVER_ERROR
        msg = Error.GENERIC_ERROR
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

    def __handle_progress(self):
        self.acquisition.upadate_progress_bar()

    def __scrape(self):
        if self.url_configuration_group_box.isEnabled() is True:
            self.url_configuration_group_box.setEnabled(False)

        # Login params
        self.url = self.label_url.text()

        self.spinner.start()
        self.setEnabled(False)

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec()

        self.__start_scraped()


    def __start_scraped(self):
        if self.acquisition_directory is None:
            self.acquisition_directory = self.case_view.form.controller.create_acquisition_directory(
                'video',
                self.configuration_general.configuration['cases_folder_path'],
                self.case_info['name'],
                self.input_url.text()
            )

        self.is_acquisition_running = True
        self.video_controller.set_url(self.input_url.text())
        self.methods_to_execute = [
            (self.checkbox_audio.isChecked(), self.video_controller.extract_audio),
            (True, self.video_controller.scrape_info),
            (True, self.video_controller.download_video),
        ]

        internal_tasks = list(filter(lambda task: task[0] == True, self.methods_to_execute))

        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(0)
        self.acquisition.start([], self.acquisition_directory, self.case_info, len(internal_tasks))

        self.status.showMessage(Logger.DOWNLOAD_VIDEO)
        self.acquisition.logger.info(Logger.DOWNLOAD_VIDEO)
        self.acquisition.info.add_task(tasks.DOWNLOAD_VIDEO, state.STARTED, status.PENDING)

        # Create acquisition folder
        title = self.video_controller.get_video_title_sanitized(self.input_url.text())
        self.url_dir = os.path.join(self.acquisition_directory, title)
        if not os.path.exists(self.url_dir):
            os.makedirs(self.url_dir)

        self.video_controller.set_dir(self.url_dir)

        self.__init_worker()

    def __hanlde_scraped(self):
        row = self.acquisition.info.get_row(tasks.DOWNLOAD_VIDEO)
        self.acquisition.info.update_task(row, state.FINISHED, status.COMPLETED, '')

        self.video_controller.create_zip(self.url_dir)

        self.__zip_and_remove(self.url_dir)

        self.acquisition.stop([], '', 1)
        self.acquisition.log_end_message()
        self.spinner.stop()

        self.acquisition.post_acquisition.execute(self.acquisition_directory, self.case_info, 'video')

    def __are_post_acquisition_finished(self):
        self.acquisition.set_completed_progress_bar()

        self.progress_bar.setHidden(True)
        self.status.showMessage('')

        self.setEnabled(True)

        self.__show_finish_acquisition_dialog()

        self.acquisition_directory = None
        self.is_acquisition_running = False

    def __show_finish_acquisition_dialog(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(Logger.ACQUISITION_FINISHED)
        msg.setText(Details.ACQUISITION_FINISHED)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)

        return_value = msg.exec()
        if return_value == QtWidgets.QMessageBox.StandardButton.Yes:
            self.__open_acquisition_directory()

    def __zip_and_remove(self, video_dir):

        shutil.make_archive(video_dir, 'zip', video_dir)

        try:
            shutil.rmtree(video_dir)
        except OSError as e:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Icon.Critical,
                                  tasks.INSTAGRAM,
                                  Error.DELETE_PROJECT_FOLDER,
                                  "Error: %s - %s." % (e.filename, e.strerror)
                                  )

            error_dlg.exec()

    def __open_acquisition_directory(self):
        os.startfile(self.acquisition_directory)

    def __on_text_changed(self):
        all_field_filled = all(input_field.text() for input_field in self.input_fields)
        self.scrape_button.setEnabled(all_field_filled)

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
