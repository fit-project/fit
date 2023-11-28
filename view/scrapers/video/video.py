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
import string
import subprocess


import requests
from PyQt6 import QtCore, QtGui, QtWidgets

from PyQt6.QtGui import QPixmap, QImage

from view.scrapers.video.form import VideoForm
from view.menu_bar import MenuBar as MenuBarView

from view.error import Error as ErrorView
from view.spinner import Spinner
from view.acquisition.acquisition import Acquisition

from controller.video import Video as VideoController

from common.constants import (
    details as Details,
    logger as Logger,
    error as Error,
)
from common.constants.view import general, video
from common.constants.view.tasks import labels, state, status
from common.utility import get_platform, resolve_path

logger_acquisition = logging.getLogger(__name__)


class VideoWorker(QtCore.QObject):
    scraped = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(object)
    valid_url = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(self, video_controller, methods_to_execute, input_url):
        super().__init__()
        self.video_controller = video_controller
        self.methods_to_execute = methods_to_execute
        self.input_url = input_url

    @QtCore.pyqtSlot()
    def run(self):
        if self.video_controller.video_id is None:
            self.video_controller.set_url(self.input_url.text())
            try:
                if not self.video_controller.is_facebook_video():
                    self.video_controller.get_video_id(self.input_url.text())
                else:
                    self.video_controller.video_id = "facebook"
            except Exception as e:
                self.error.emit(
                    {"title": video.INVALID_URL, "msg": Error.INVALID_URL, "details": e}
                )
            else:
                self.valid_url.emit()
        else:
            for checkbox, method in self.methods_to_execute:
                if checkbox:
                    try:
                        method()
                    except Exception as e:
                        self.error.emit(
                            {
                                "title": video.INVALID_URL,
                                "msg": Error.INVALID_URL,
                                "details": e,
                            }
                        )
                    else:
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

        self.setWindowIcon(
            QtGui.QIcon(os.path.join(resolve_path("assets/svg/"), "FIT.svg"))
        )

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

        self.form = VideoForm(self.centralwidget)
        self.form.load_button.clicked.connect(self.__load)

        self.status = QtWidgets.QStatusBar()
        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(517, 340, 131, 23))
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setHidden(True)
        self.status.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.status)

        # SCRAPE BUTTON
        self.scrape_button = QtWidgets.QPushButton(self.centralwidget)
        self.scrape_button.setGeometry(QtCore.QRect(865, 385, 80, 25))
        self.scrape_button.setObjectName("scrapeButton")
        self.scrape_button.setFont(font)
        self.scrape_button.clicked.connect(self.__scrape)
        self.scrape_button.setEnabled(False)

        self.configuration_general = self.menu_bar.configuration_view.get_tab_from_name(
            "configuration_general"
        )

        # Get timestamp parameters
        self.configuration_timestamp = (
            self.menu_bar.configuration_view.get_tab_from_name(
                "configuration_timestamp"
            )
        )

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
        self.scrape_button.setText(general.DOWNLOAD)

    def __init_worker(self):
        self.thread_worker = QtCore.QThread()
        self.worker = VideoWorker(
            self.video_controller, self.methods_to_execute, self.input_url
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

        title = video.SERVER_ERROR
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
        self.video_controller.video_id = None
        center_x = self.x() + self.width / 2
        center_y = self.y() + self.height / 2
        self.spinner.set_position(center_x, center_y)
        self.spinner.start()

        self.quality.clear()
        self.setEnabled(False)

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec()
        if self.video_controller.video_id is None:
            self.__init_worker()
            self.acquisition_group_box.setEnabled(True)
        else:
            self.acquisition_group_box.setEnabled(True)
            self.__start_scraped()

    def __scrape(self):
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
        if self.video_controller.video_id is None:
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
        try:
            title, thumbnail, duration = self.video_controller.print_info()
        except Exception as e:
            title = video.SERVER_ERROR
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
        else:
            pixmap = QPixmap()
            if thumbnail is False:
                qimage = QImage(resolve_path("assets/images/no-preview.png"))
                pixmap = QPixmap.fromImage(qimage)
            else:
                response = requests.get(thumbnail)
                pixmap.loadFromData(response.content)
            self.thumbnail.setPixmap(pixmap)
            self.title.setText(title)
            self.label_duration.show()
            self.duration.setText(duration)
            self.scrape_button.setEnabled(True)

            if not self.video_controller.is_youtube_video():
                self.checkbox_comments.setEnabled(False)
                self.checkbox_subtitles.setEnabled(False)

            # check if audio only is available for download
            audio_available = self.video_controller.is_audio_available()
            if not audio_available:
                self.checkbox_audio.setEnabled(False)

            # get the list of supported quality
            unique_items = set()
            availabe_resolution = self.video_controller.get_available_resolutions()
            if availabe_resolution == "Default":
                self.quality.addItem(availabe_resolution)
            else:
                for format in availabe_resolution:
                    if "format_note" in format:
                        format_id = format["format_id"]
                        if "format_note" in format:
                            format_desc = format["format_note"]
                            self.quality.addItem(f"{format_id}: {format_desc}")
                            unique_items.add(format_id)
                    else:
                        if "Default" not in unique_items:
                            self.quality.addItem("Default")
                            unique_items.add("Default")

        self.spinner.stop()
        self.is_acquisition_running = False

    def __start_scraped(self):
        if self.acquisition_directory is None:
            self.acquisition_directory = (
                self.menu_bar.case_view.form.controller.create_acquisition_directory(
                    "video",
                    self.configuration_general.configuration["cases_folder_path"],
                    self.case_info["name"],
                    self.input_url.text(),
                )
            )
        self.url_dir = os.path.join(
            self.acquisition_directory, self.video_controller.id_digest
        )
        self.is_acquisition_running = True

        self.video_controller.set_quality(self.quality.currentText())

        self.methods_to_execute = [
            (True, self.video_controller.get_info),
            (True, self.video_controller.download_video),
            (self.checkbox_audio.isChecked(), self.video_controller.get_audio),
            (self.checkbox_thumbnail.isChecked(), self.video_controller.get_thumbnail),
            (self.checkbox_subtitles.isChecked(), self.video_controller.get_subtitles),
            (self.checkbox_comments.isChecked(), self.video_controller.get_comments),
        ]

        internal_tasks = list(
            filter(lambda task: task[0] is True, self.methods_to_execute)
        )

        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(0)
        self.acquisition.start(
            [], self.acquisition_directory, self.case_info, len(internal_tasks)
        )

        self.status.showMessage(Logger.DOWNLOAD_VIDEO)
        self.acquisition.logger.info(Logger.DOWNLOAD_VIDEO)
        self.acquisition.info.add_task(
            labels.DOWNLOAD_VIDEO, state.STARTED, status.PENDING
        )

        if not os.path.exists(self.url_dir):
            os.makedirs(self.url_dir)

        self.video_controller.set_dir(self.url_dir)

        self.__init_worker()

    def __hanlde_scraped(self):
        row = self.acquisition.info.get_row(labels.DOWNLOAD_VIDEO)
        self.acquisition.info.update_task(row, state.COMPLETED, status.SUCCESS, "")

        self.video_controller.create_zip(self.url_dir)

        self.__zip_and_remove(self.url_dir)

        self.acquisition.stop([], "", 1)
        self.acquisition.log_end_message()
        self.spinner.stop()

        self.acquisition.post_acquisition.execute(
            self.acquisition_directory, self.case_info, "video"
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
                labels.DOWNLOAD_VIDEO,
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

    def __back_to_wizard(self):
        if self.is_acquisition_running is False:
            self.deleteLater()
            self.wizard.reload_case_info()
            self.wizard.show()

    def closeEvent(self, event):
        event.ignore()
        self.__back_to_wizard()
