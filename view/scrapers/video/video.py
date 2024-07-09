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
import subprocess
import requests

from PyQt6 import QtCore, QtGui, QtWidgets

from PyQt6.QtGui import QPixmap, QImage


from view.scrapers.video.form import VideoForm
from view.scrapers.video.acquisition import VideoAcquisition
from view.menu_bar import MenuBar as MenuBarView

from view.spinner import Spinner

from controller.configurations.tabs.general.general import (
    General as GeneralConfigurationController,
)
from controller.case import Case as CaseController


from common.constants import details, logger
from common.constants.view import general
from common.constants.view.tasks import status
from common.utility import get_platform, resolve_path


class Video(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Video, self).__init__(*args, **kwargs)
        self.spinner = Spinner()

    def init(self, case_info, wizard, options=None):
        self.acquisition_directory = None
        self.id_digest = None
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

        # DOWNLOAD BUTTON
        self.download_button = QtWidgets.QPushButton(self.centralwidget)
        self.download_button.setGeometry(QtCore.QRect(865, 385, 80, 25))
        self.download_button.setObjectName("download_button")
        self.download_button.setFont(font)
        self.download_button.clicked.connect(self.__download)
        self.download_button.setEnabled(False)

        # ACQUISITION
        self.is_acquisition_running = False
        self.acquisition_manager = VideoAcquisition(
            logging.getLogger(__name__),
            self.progress_bar,
            self.status,
            self,
        )

        self.acquisition_manager.start_tasks_is_finished.connect(
            self.__start_task_is_finished
        )

        self.acquisition_manager.load_finished.connect(self.__is_load_finished)

        self.acquisition_manager.progress.connect(self.__handle_progress)

        self.acquisition_manager.post_acquisition_is_finished.connect(
            self.__acquisition_is_finished
        )

        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(general.MAIN_WINDOW_TITLE)
        self.download_button.setText(general.DOWNLOAD)

    def __load(self):
        self.__enable_all(False)
        self.__start_spinner()
        self.form.quality.clear()

        if self.is_task_started is False:
            self.__start_task()
        else:
            self.acquisition_manager.load()

    def __is_load_finished(self, __status, info):
        self.spinner.stop()
        self.__enable_all(True)

        if __status == status.SUCCESS:
            pixmap = QPixmap()

            thumbnail = info.get("thumbnail")
            title = info.get("title")
            duration = info.get("duration")
            is_youtube_video = info.get("is_youtube_video")
            audio_available = info.get("audio_available")
            availabe_resolution = info.get("availabe_resolution")
            self.id_digest = info.get("id_digest")

            if thumbnail is False:
                qimage = QImage(resolve_path("assets/images/no-preview.png"))
                pixmap = QPixmap.fromImage(qimage)
            else:
                response = requests.get(thumbnail)
                pixmap.loadFromData(response.content)
            self.form.thumbnail.setPixmap(pixmap)
            self.form.title.setText(title)
            self.form.label_duration.show()
            self.form.duration.setText(duration)

            if not is_youtube_video:
                self.form.checkbox_comments.setEnabled(False)
                self.form.checkbox_subtitles.setEnabled(False)

            # check if audio only is available for download
            if not audio_available:
                self.form.checkbox_audio.setEnabled(False)

            # get the list of supported quality
            unique_items = set()
            if availabe_resolution == "Default":
                self.form.quality.addItem(availabe_resolution)
            else:
                for format in availabe_resolution:
                    if "format_note" in format:
                        format_id = format["format_id"]
                        if "format_note" in format:
                            format_desc = format["format_note"]
                            self.form.quality.addItem(f"{format_id}: {format_desc}")
                            unique_items.add(format_id)
                    else:
                        if "Default" not in unique_items:
                            self.form.quality.addItem("Default")
                            unique_items.add("Default")

            self.form.acquisition_group_box.setEnabled(True)
            self.download_button.setEnabled(True)
        else:
            pass

    def __start_task(self):
        if self.acquisition_directory is None:
            # Create acquisition directory
            self.acquisition_directory = CaseController().create_acquisition_directory(
                "video",
                GeneralConfigurationController().configuration["cases_folder_path"],
                self.case_info["name"],
                self.form.input_url.text(),
            )

        if self.acquisition_directory is not None:
            if self.is_task_started is False:
                self.acquisition_manager.options = {
                    "acquisition_directory": self.acquisition_directory,
                    "type": "video",
                    "case_info": self.case_info,
                    "url": self.form.input_url.text(),
                }
                self.acquisition_manager.load_tasks()
                self.acquisition_manager.start()

    def __start_task_is_finished(self):
        self.is_task_started = True
        self.__load()

    def __download(self):
        self.is_acquisition_running = True
        self.progress_bar.setHidden(False)
        self.progress_bar.setValue(0)
        self.__enable_all(False)
        self.__start_spinner()

        methods_to_execute = ["get_info", "download_video"]
        checkboxes = self.form.acquisition_group_box.findChildren(QtWidgets.QCheckBox)
        checkboxes_checked = list(
            filter(lambda checkbox: checkbox.isChecked(), checkboxes)
        )
        for checkbox in checkboxes_checked:
            methods_to_execute.append(checkbox.objectName())

        self.acquisition_manager.options["methods_to_execute"] = methods_to_execute
        self.increment = 100 / len(methods_to_execute)

        # Create acquisition folder
        url_dir = os.path.join(
            self.acquisition_directory,
            self.id_digest,
        )
        if not os.path.exists(url_dir):
            os.makedirs(url_dir)

        self.acquisition_manager.options["url_dir"] = url_dir

        self.acquisition_manager.download()

    def __acquisition_is_finished(self):
        self.spinner.stop()
        self.__enable_all(True)

        self.progress_bar.setHidden(True)
        self.status.showMessage("")
        self.acquisition_manager.log_end_message()
        self.acquisition_manager.set_completed_progress_bar()
        self.acquisition_manager.unload_tasks()

        self.download_button.setEnabled(False)
        self.form.acquisition_group_box.setEnabled(False)
        self.form.quality.clear()

        self.__show_finish_acquisition_dialog()

        self.acquisition_directory = None
        self.id_digest = None
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
