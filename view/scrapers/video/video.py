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
import requests

from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtGui import QPixmap, QImage

from view.clickable_label import ClickableLabel as ClickableLabelView

from view.scrapers.video.acquisition import VideoAcquisition
from view.spinner import Spinner

from view.util import (
    show_configuration_dialog,
    show_case_info_dialog,
    show_finish_acquisition_dialog,
    show_acquisition_info_dialog,
)


from controller.configurations.tabs.general.general import (
    General as GeneralConfigurationController,
)
from controller.case import Case as CaseController

from common.constants.view import general, video
from common.constants.view.tasks import status
from common.utility import resolve_path, get_version


class Video(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Video, self).__init__(*args, **kwargs)
        self.spinner = Spinner()
        self.__init_ui()

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/video/video.ui"), self)

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

        # PREVIEW CONTAINER
        self.preview_container.setEnabled(False)

        # ACQUISITION CRITERIA CONTAINER
        self.acquisition_criteria.setEnabled(False)

        supported_site = ClickableLabelView(video.SUPPORTED_SITES_LIST, video.SUPPORTED)
        supported_site.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.url_configuration_top_layout.addWidget(supported_site)

        # MULTIFUNCTION BUTTON
        self.multifunction_button.setEnabled(False)
        self.multifunction_button.clicked.connect(self.__select_task)

        self.input_url.textEdited.connect(self.__remove_white_space)
        self.input_url.textChanged.connect(self.__enable_multifunction_button)

        self.__uncheck_checkboxes()

    def __select_task(self):
        sender = self.sender()
        if sender.text() == general.BUTTON_LOAD:
            self.__load()
        elif sender.text() == general.DOWNLOAD:
            self.__download()

    def __swap_button_text(self):
        if self.multifunction_button.text() == general.BUTTON_LOAD:
            self.multifunction_button.setText(general.DOWNLOAD)
        elif self.multifunction_button.text() == general.DOWNLOAD:
            self.multifunction_button.setText(general.BUTTON_LOAD)

    def __remove_white_space(self, text):
        sender = self.sender()
        sender.setText(text.replace(" ", ""))

    def __enable_multifunction_button(self, text):
        self.multifunction_button.setEnabled(bool(text))

    def __uncheck_checkboxes(self):
        for checkbox in self.acquisition_criteria.findChildren(QtWidgets.QCheckBox):
            if checkbox.isChecked():
                checkbox.setChecked(False)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_window(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def init(self, case_info, wizard, options=None):
        self.acquisition_directory = None
        self.id_digest = None
        self.is_task_started = False
        self.is_acquisition_running = False
        self.case_info = case_info
        self.wizard = wizard

        self.case_button.clicked.connect(lambda: show_case_info_dialog(self.case_info))

        # ACQUISITION
        self.is_acquisition_running = False
        self.acquisition_manager = VideoAcquisition(
            logging.getLogger(__name__),
            self.progress_bar,
            self.status_message,
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

    def __load(self):
        self.__enable_all(False)
        self.__start_spinner()
        self.video_quality.clear()

        if self.is_task_started is False:
            self.__start_task()
        else:
            self.acquisition_manager.load()

    def __is_load_finished(self, __status, info):
        self.spinner.stop()
        self.__enable_all(True)

        if __status == status.SUCCESS:
            self.preview_container.setEnabled(True)

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

            self.preview_thumbnail.setPixmap(
                pixmap.scaled(
                    self.preview_thumbnail.maximumWidth(),
                    self.preview_thumbnail.maximumHeight(),
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.preview_title.setText(video.VIDEO_TITLE.format(title))
            self.preview_duration.setText(video.DURATION.format(duration))

            if not is_youtube_video:
                self.get_comments.setEnabled(False)
                self.get_subtitles.setEnabled(False)

            # check if audio only is available for download
            if not audio_available:
                self.get_audio.setEnabled(False)

            # get the list of supported quality
            unique_items = set()
            if availabe_resolution == "Default":
                self.video_quality.addItem(availabe_resolution)
            else:
                for format in availabe_resolution:
                    if "format_note" in format:
                        format_id = format["format_id"]
                        if "format_note" in format:
                            format_desc = format["format_note"]
                            self.video_quality.addItem(f"{format_id}: {format_desc}")
                            unique_items.add(format_id)
                    else:
                        if "Default" not in unique_items:
                            self.video_quality.addItem("Default")
                            unique_items.add("Default")

            self.acquisition_criteria.setEnabled(True)
            self.__swap_button_text()

    def __start_task(self):
        if self.acquisition_directory is None:
            # Create acquisition directory
            self.acquisition_directory = CaseController().create_acquisition_directory(
                "video",
                GeneralConfigurationController().configuration["cases_folder_path"],
                self.case_info["name"],
                self.input_url.text(),
            )

        if self.acquisition_directory is not None:
            if self.is_task_started is False:
                self.acquisition_manager.options = {
                    "acquisition_directory": self.acquisition_directory,
                    "type": "video",
                    "case_info": self.case_info,
                    "url": self.input_url.text(),
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
        checkboxes = self.acquisition_criteria.findChildren(QtWidgets.QCheckBox)
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
        self.status_message.setText("")
        self.acquisition_manager.log_end_message()
        self.acquisition_manager.set_completed_progress_bar()
        self.acquisition_manager.unload_tasks()

        self.__swap_button_text()
        self.video_quality.clear()
        self.__uncheck_checkboxes()
        self.preview_thumbnail.clear()
        self.preview_title.clear()
        self.preview_duration.clear()
        self.input_url.clear()

        self.acquisition_criteria.setEnabled(False)
        self.preview_container.setEnabled(False)
        self.multifunction_button.setEnabled(True)

        show_finish_acquisition_dialog(self.acquisition_directory)

        self.acquisition_directory = None
        self.id_digest = None
        self.is_task_started = False
        self.is_acquisition_running = False

    def __handle_progress(self):
        self.progress_bar.setValue(self.progress_bar.value() + int(self.increment))

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
