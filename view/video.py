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
import webbrowser

import requests
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QLabel

from view.menu_bar import MenuBar as MenuBarView

from view.error import Error as ErrorView
from view.spinner import Spinner
from view.acquisition.acquisition import Acquisition

from controller.video import Video as VideoController

from common.constants import (
    details as Details,
    logger as Logger,
    tasks,
    state,
    status,
    error as Error,
)
from common.constants.view import general, video
from common.utility import get_platform

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


# Create a clickable label to open the browser
class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("color: #0067C0;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            url = video.SUPPORTED_SITES_LIST
            webbrowser.open(url)

    def enterEvent(self, event):
        self.setStyleSheet("color: #0067C0; text-decoration: underline;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def leaveEvent(self, event):
        self.setStyleSheet("color: #0067C0; text-decoration: none;")


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

        # VIDEO CONFIGURATION GROUP BOX
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
        self.input_url.textEdited.connect(self.__validate_input)
        self.input_url.setPlaceholderText(video.PLACEHOLDER_URL)

        # SUPPORTED SITES
        self.label_supported_sites = ClickableLabel(self.url_configuration_group_box)
        self.label_supported_sites.setGeometry(QtCore.QRect(250, 120, 150, 20))
        self.label_supported_sites.setFont(font)
        self.label_supported_sites.setObjectName("label_supported_sites")

        # AUTH
        """self.label_username = QtWidgets.QLabel(self.url_configuration_group_box)
        self.label_username.setGeometry(QtCore.QRect(20, 120, 80, 20))
        self.label_username.setFont(font)
        self.label_username.setObjectName("label_username")

        self.input_username = QtWidgets.QLineEdit(self.url_configuration_group_box)
        self.input_username.setGeometry(QtCore.QRect(100, 120, 290, 20))
        self.input_username.setFont(font)
        self.input_username.setObjectName("input_username")
        self.input_username.setPlaceholderText(video.PLACEHOLDER_USERNAME)

        self.label_password = QtWidgets.QLabel(self.url_configuration_group_box)
        self.label_password.setGeometry(QtCore.QRect(20, 160, 80, 20))
        self.label_password.setFont(font)
        self.label_password.setObjectName("label_password")

        self.input_password = QtWidgets.QLineEdit(self.url_configuration_group_box)
        self.input_password.setGeometry(QtCore.QRect(100, 160, 290, 20))
        self.input_password.setFont(font)
        self.input_password.setObjectName("input_password")
        self.input_password.setPlaceholderText(video.PLACEHOLDER_PASSWORD)
        self.input_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)"""

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

        # VIDEO QUALITY
        self.label_video_quality = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_video_quality.setGeometry(QtCore.QRect(20, 30, 111, 20))
        self.label_video_quality.setFont(font)
        self.label_video_quality.setObjectName("label_video_quality")

        self.quality = QtWidgets.QComboBox(self.acquisition_group_box)
        self.quality.setGeometry(QtCore.QRect(20, 70, 111, 25))
        self.quality.setFont(font)
        self.quality.setObjectName("quality")

        # ADDITIONAL_INFORMATION
        self.label_additional_information = QtWidgets.QLabel(self.acquisition_group_box)
        self.label_additional_information.setGeometry(QtCore.QRect(180, 30, 150, 20))
        self.label_additional_information.setFont(font)
        self.label_additional_information.setObjectName("label_additional_information")

        self.checkbox_audio = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_audio.setGeometry(QtCore.QRect(180, 50, 100, 17))
        self.checkbox_audio.setFont(font)
        self.checkbox_audio.setObjectName("checkbox_audio")

        self.checkbox_thumbnail = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_thumbnail.setGeometry(QtCore.QRect(180, 70, 100, 17))
        self.checkbox_thumbnail.setFont(font)
        self.checkbox_thumbnail.setObjectName("checkbox_thumbnail")

        self.checkbox_subtitles = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_subtitles.setGeometry(QtCore.QRect(180, 90, 230, 17))
        self.checkbox_subtitles.setFont(font)
        self.checkbox_subtitles.setObjectName("checkbox_subtitles")

        self.checkbox_comments = QtWidgets.QCheckBox(self.acquisition_group_box)
        self.checkbox_comments.setGeometry(QtCore.QRect(180, 110, 230, 17))
        self.checkbox_comments.setFont(font)
        self.checkbox_comments.setObjectName("checkbox_comments")

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

        # VIDEO PREVIEW GROUP BOX
        self.video_preview_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.video_preview_group_box.setEnabled(True)
        self.video_preview_group_box.setFont(font)
        self.video_preview_group_box.setGeometry(QtCore.QRect(515, 20, 430, 360))
        self.video_preview_group_box.setObjectName("video_preview_group_box")

        self.thumbnail = QLabel(self.video_preview_group_box)
        self.thumbnail.setGeometry(QtCore.QRect(30, 40, 370, 208))
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setObjectName("thumbnail")

        self.title = QtWidgets.QLabel(self.video_preview_group_box)
        self.title.setGeometry(QtCore.QRect(30, 260, 370, 60))
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.title.setWordWrap(True)

        self.label_duration = QtWidgets.QLabel(self.video_preview_group_box)
        self.label_duration.setGeometry(QtCore.QRect(30, 330, 60, 25))
        self.label_duration.setFont(font)
        self.label_duration.hide()
        self.label_duration.setObjectName("label_duration")

        self.duration = QtWidgets.QLabel(self.video_preview_group_box)
        self.duration.setGeometry(QtCore.QRect(90, 330, 50, 25))
        self.duration.setFont(font)
        self.duration.setObjectName("duration")

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
        self.url_configuration_group_box.setTitle(video.URL_CONFIGURATION)
        self.video_preview_group_box.setTitle(video.PREVIEW)
        self.label_url.setText(video.URL)
        self.label_supported_sites.setText(video.SUPPORTED)
        # self.label_username.setText(video.LABEL_USERNAME)
        # self.label_password.setText(video.LABEL_PASSWORD)
        self.scrape_button.setText(general.DOWNLOAD)
        self.label_duration.setText(video.DURATION)
        self.acquisition_group_box.setTitle(video.ACQUISITON_SETTINGS)
        self.label_video_quality.setText("<strong>" + video.VIDEO_QUALITY + "</strong>")
        self.label_additional_information.setText(
            "<strong>" + video.ADDITIONAL_INFORMATION + "</strong>"
        )
        self.checkbox_audio.setText(video.AUDIO)
        self.checkbox_thumbnail.setText(video.THUMBNAIL)
        self.checkbox_subtitles.setText(video.SUBTITLES)
        self.checkbox_comments.setText(video.COMMENTS)
        self.load_button.setText(general.BUTTON_LOAD)
        self.scrape_button.setText(general.DOWNLOAD)

    def __validate_input(self, text):
        sender = self.sender()
        sender.setText(text.replace(" ", ""))

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
                qimage = QImage("assets/images/no-preview.png")
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
            tasks.DOWNLOAD_VIDEO, state.STARTED, status.PENDING
        )

        if not os.path.exists(self.url_dir):
            os.makedirs(self.url_dir)

        self.video_controller.set_dir(self.url_dir)

        self.__init_worker()

    def __hanlde_scraped(self):
        row = self.acquisition.info.get_row(tasks.DOWNLOAD_VIDEO)
        self.acquisition.info.update_task(row, state.FINISHED, status.COMPLETED, "")

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
