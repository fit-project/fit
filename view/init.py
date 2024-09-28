#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import subprocess

from PyQt6 import QtCore, QtWidgets, QtWebEngineWidgets, QtGui, uic

from view.error import Error as ErrorView
from view.dialog import Dialog, DialogButtonTypes
from view.clickable_label import ClickableLabel as ClickableLabelView
from view.audio_recorder_checker import AudioRecorderChecker
from view.util import (
    screens_changed,
    ScreensChangedType,
)

from controller.configurations.tabs.packetcapture.packetcapture import PacketCapture
from controller.configurations.tabs.network.networktools import NetworkTools
from controller.configurations.tabs.screenrecorder.screenrecorder import ScreenRecorder


from common.utility import *
from common.constants.view.init import *
from common.constants.view.general import *
from common.constants.view.tasks import status


class DownloadAndInstallNpcap(QtWidgets.QDialog):
    finished = QtCore.pyqtSignal(dict)

    def __init__(self, url, parent=None):
        super(DownloadAndInstallNpcap, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.path = None

        self.progress_dialog = Dialog(
            NPCAP,
            NPCAP_DOWNLOAD,
        )
        self.progress_dialog.message.setStyleSheet("font-size: 13px;")
        self.progress_dialog.set_buttons_type(DialogButtonTypes.NONE)
        self.progress_dialog.show_progress_bar()
        self.progress_dialog.progress_bar.setValue(0)

        self.web_view = QtWebEngineWidgets.QWebEngineView()
        self.web_view.page().profile().downloadRequested.connect(
            self.on_download_requested
        )

        self.web_view.load(QtCore.QUrl(url))
        self.web_view.hide()

    def on_download_requested(self, download):
        old_path = download.url().path()
        suffix = QtCore.QFileInfo(old_path).suffix()
        self.path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", old_path, "*." + suffix
        )

        if self.path:
            download.setDownloadFileName(self.path)
            download.accept()
            download.isFinishedChanged.connect(self.__install)
            download.receivedBytesChanged.connect(
                lambda: self.__progress(
                    download.receivedBytes(),
                    download.totalBytes(),
                )
            )
            download.totalBytesChanged.connect(
                lambda: self.__progress(
                    download.receivedBytes(),
                    download.totalBytes(),
                )
            )
            self.progress_dialog.show()
        else:
            self.reject()

    def __install(self):

        self.close()
        self.progress_dialog.close()

        __status = status.SUCCESS
        details = ""

        cmd = 'Powershell -Command Start-Process "{}" -Verb RunAs'.format(self.path)
        try:
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            process.check_returncode()
        except Exception as e:
            __status = status.FAIL
            details = str(e)

        self.finished.emit(
            {
                "status": __status,
                "details": details,
            }
        )

    def __progress(self, bytes_received, bytes_total):
        if bytes_total > 0:
            download_percentage = int(bytes_received * 100 / bytes_total)
            self.progress_dialog.progress_bar.setValue(download_percentage)


class Init(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__set_initial_screen_to_record_information()

    def __quit(self):
        sys.exit(1)

    def __set_initial_screen_to_record_information(self):
        app = QtWidgets.QApplication.instance()

        app.screenAdded.connect(lambda: screens_changed(ScreensChangedType.ADDED))
        app.screenRemoved.connect(lambda: screens_changed(ScreensChangedType.REMOVED))
        app.primaryScreenChanged.connect(
            lambda: screens_changed(ScreensChangedType.PRIMARY_SCREEN_CHANGED)
        )

    def __enable_network_functionality(self):
        configuration = NetworkTools().configuration
        if configuration.get("traceroute") is False:
            configuration["traceroute"] = True
            NetworkTools().configuration = configuration

        options = PacketCapture().options
        if options.get("enabled") is False:
            options["enabled"] = True
            PacketCapture().options = options

    def __disable_network_functionality(self, dialog=None):
        if dialog:
            dialog.close()

        configuration = NetworkTools().configuration
        if configuration.get("traceroute") is True:
            configuration["traceroute"] = False
            NetworkTools().configuration = configuration

        options = PacketCapture().options
        if options.get("enabled") is True:
            options["enabled"] = False
            PacketCapture().options = options

    def __download_npcap(self, dialog=None):
        if dialog:
            dialog.close()
        try:
            url = get_npcap_installer_url()
            self.donwload_and_install = DownloadAndInstallNpcap(url)
            self.donwload_and_install.rejected.connect(self.__download_rejected)
            self.donwload_and_install.finished.connect(
                self.__donwload_and_install_finished
            )
            self.donwload_and_install.exec()
        except Exception as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                NPCAP,
                ERR_NPCAP_RELEASE_VERSION,
                str(e),
            )
            error_dlg.exec()

    def __download_rejected(self):
        self.__disable_network_functionality()

    def __donwload_and_install_finished(self, result):
        if result.get("status") == status.SUCCESS:
            self.__enable_network_functionality()
        else:
            self.__disable_network_functionality()
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                NPCAP,
                NPCAP_ERROR_DURING_INSTALLATION,
                result.get("details"),
            )
            error_dlg.exec()

    def __download_and_install_ffmpeg(self, dialog=None):
        is_ffmpeg_installed = False

        if dialog:
            dialog.close()

        ffmpeg_istaller = "ffdl-gui"
        if is_cmd(ffmpeg_istaller):
            result = subprocess.run(ffmpeg_istaller, stdout=subprocess.DEVNULL)
            if result.returncode == 0:
                is_ffmpeg_installed = True

        if is_ffmpeg_installed is True:
            self.__enable_screen_recorder_functionality()

    def init_check(self):
        # Check internet connection
        if check_internet_connection() is False:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                CHECK_CONNETION,
                ERR_INTERNET_DISCONNECTED,
                "",
            )
            error_dlg.message.setStyleSheet("font-size: 13px;")
            error_dlg.right_button.clicked.connect(self.__quit)

            error_dlg.exec()

        if is_admin() is False:

            dialog = Dialog(
                USER_IS_NOT_ADMIN_TITLE,
                USER_IS_NOT_ADMIN_MSG,
            )
            dialog.message.setStyleSheet("font-size: 13px;")
            dialog.set_buttons_type(DialogButtonTypes.QUESTION)
            dialog.right_button.clicked.connect(
                lambda: self.__disable_network_functionality(dialog)
            )
            dialog.left_button.clicked.connect(self.__quit)

            dialog.content_box.adjustSize()

            dialog.exec()

        if ScreenRecorder().options.get("show_arc_window_at_startup") is True:
            AudioRecorderChecker().exec()
            # Mostra la finestra

        if get_platform() == "win":
            if is_npcap_installed() is False and is_admin():
                dialog = Dialog(
                    NPCAP,
                    WAR_NPCAP_NOT_INSTALLED,
                )
                dialog.message.setStyleSheet("font-size: 13px;")
                dialog.set_buttons_type(DialogButtonTypes.QUESTION)
                dialog.right_button.clicked.connect(
                    lambda: self.__disable_network_functionality(dialog)
                )
                dialog.left_button.clicked.connect(
                    lambda: self.__download_npcap(dialog)
                )

                dialog.exec()

        # I need to review the UI
        if getattr(sys, "frozen", False) and is_there_a_new_portable_version():
            parser = ConfigParser()
            parser.read(resolve_path("assets/config.ini"))
            url = parser.get("fit_properties", "fit_latest_download_url")

            dialog = Dialog(
                FIT_NEW_VERSION_DOWNLOAD,
                FIT_NEW_VERSION_MSG,
            )
            dialog.right_button.clicked.connect(dialog.close)
            dialog.message.setStyleSheet("font-size: 13px;")
            dialog.message.hide()
            dialog.details.hide()
            clickable_label_layout = QtWidgets.QHBoxLayout()
            clickable_label_layout.setSpacing(0)
            clickable_label_layout.addWidget(
                QtWidgets.QLabel(
                    "There is a new version of FIT. You can download it from: "
                )
            )

            clickable_label_layout.addWidget(
                ClickableLabelView(
                    url, '<strong style="color:red"><i><u>here</u></i></strong>'
                )
            )
            horizontal_spacer = QtWidgets.QSpacerItem(
                20,
                40,
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding,
            )
            clickable_label_layout.addItem(horizontal_spacer)

            dialog.text_box.addLayout(clickable_label_layout)

            dialog.content_box.adjustSize()

            dialog.exec()
