#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import subprocess
import psutil
import time
import shutil

from PyQt6 import QtCore, QtWidgets, QtWebEngineWidgets

from view.error import Error as ErrorView
from view.dialog import Dialog, DialogButtonTypes
from view.clickable_label import ClickableLabel as ClickableLabelView

from controller.configurations.tabs.packetcapture.packetcapture import PacketCapture
from controller.configurations.tabs.network.networktools import NetworkTools


from common.utility import *
from common.constants.view.init import *
from common.constants.view.general import *
from common.constants.view.tasks import status


class DownloadAndSave(QtWidgets.QDialog):
    finished = QtCore.pyqtSignal(str)

    def __init__(self, url, progress_dialog_title, progress_dialog_message,  parent=None):
        super(DownloadAndSave, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.file_path = None
        
        self.filename = QtCore.QUrl(url).path()
        self.suffix = QtCore.QFileInfo(self.filename).suffix()

        self.progress_dialog = Dialog(
            progress_dialog_title,
            progress_dialog_message,
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
        self.file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", self.filename, "*." + self.suffix
        )

        if self.file_path:
            download.setDownloadFileName(self.file_path)
            download.accept()
            download.isFinishedChanged.connect(self.__is_download_finished)
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
    
    def __is_download_finished(self):
        self.close()
        self.progress_dialog.close()
        self.finished.emit(self.file_path)

    def __progress(self, bytes_received, bytes_total):
        if bytes_total > 0:
            download_percentage = int(bytes_received * 100 / bytes_total)
            self.progress_dialog.progress_bar.setValue(download_percentage)


class Init(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def __quit(self):
        sys.exit(1)

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

            self.ncap_process_name = QtCore.QUrl(url).path().split('/')[-1]

            donwload_and_save = DownloadAndSave(url,  NPCAP, NPCAP_DOWNLOAD)
            donwload_and_save.rejected.connect(self.__disable_network_functionality)
            donwload_and_save.finished.connect(self.__install_ncap)
            donwload_and_save.exec()
        except Exception as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                NPCAP,
                ERR_NPCAP_RELEASE_VERSION,
                str(e),
            )
            error_dlg.exec()

    def __install_ncap(self, file_path):
        cmd = 'Powershell -Command Start-Process "{}" -Verb RunAs'.format(file_path)
        try:
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            process.check_returncode()
            self.__monitoring_npcap_process_installer()
        except Exception as e:
            self.__disable_network_functionality()
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                NPCAP,
                NPCAP_ERROR_DURING_INSTALLATION,
                str(e),
            )
            error_dlg.exec()

    def __monitoring_npcap_process_installer(self):
        pid = None
        __is_npcap_installed = False

        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == self.ncap_process_name:
                pid = proc.info["pid"]
                break

        if pid is not None:
            try:
                proc = psutil.Process(pid)
                while True:
                    if not proc.is_running():
                        __is_npcap_installed = is_npcap_installed()
                        break
                    time.sleep(1)
            except psutil.NoSuchProcess as e:
                raise Exception(e)
            except Exception as e:
                raise Exception(e)
        
        if __is_npcap_installed is False:
            self.__disable_network_functionality()
        else:
            self.__enable_network_functionality()

    def __download_portable_version(self, dialog=None):
        if dialog:
            dialog.close()
        try:
            url = get_portable_download_url()
            if url is None:
                raise ValueError(DOWNLOAD_URL_ERROR)
            donwload_and_save = DownloadAndSave(url,  FIT_NEW_VERSION_DOWNLOAD_TITLE, FIT_NEW_VERSION_DOWNLOAD_MSG)
            donwload_and_save.finished.connect(self.__unzip_portable_zipfile)
            donwload_and_save.exec()
        except Exception as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                FIT_NEW_VERSION_DOWNLOAD_TITLE,
                FIT_NEW_VERSION_DOWNLOAD_ERROR,
                str(e),
            )
            error_dlg.exec()
    
    def __unzip_portable_zipfile(self, file_path):
        unzip_path = os.path.splitext(file_path)[0]
        try:
            shutil.unpack_archive(file_path, unzip_path)
            self.__execute_portable_version(unzip_path)
        except Exception as e:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                FIT_NEW_VERSION_DOWNLOAD_TITLE,
                FIT_NEW_VERSION_UNZIP_ERROR,
                str(e),
            )
            error_dlg.exec()
    
    def __execute_portable_version(self, path):

        excutable = None
        if get_platform() == "win":
            excutable = os.path.join(path, "fit.exe")

        current_directory = os.getcwd()

        if excutable is not None:
            # Change working directory
            os.chdir(path)
            cmd = 'Powershell -Command Start-Process "{}" -Verb RunAs'.format(excutable)
            try:
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                )
                process.check_returncode()
                self.__quit()
            except Exception as e:
                # Change working directory
                os.chdir(current_directory)
                error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                FIT_NEW_VERSION_DOWNLOAD_TITLE,
                FIT_NEW_VERSION_EXCUTE_ERROR,
                str(e),
            )
            error_dlg.exec()
        
        else:
            error_dlg = ErrorView(
                QtWidgets.QMessageBox.Icon.Critical,
                FIT_NEW_VERSION_DOWNLOAD_TITLE,
                FIT_NEW_VERSION_EXCUTE_ERROR,
                "No excutable path found",
            )
            error_dlg.exec()

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

        # Check admin privileges
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

        if get_platform() == "win":
            # Check if NPCAP is installed
            if is_npcap_installed() is False:
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
        
        # Check there is a new portable version of FIT
        if getattr(sys, "frozen", False) and has_new_portable_version():
            dialog = Dialog(
                    FIT_NEW_VERSION_TITLE,
                    FIT_NEW_VERSION_MSG,
                )
            dialog.message.setStyleSheet("font-size: 13px;")
            dialog.set_buttons_type(DialogButtonTypes.QUESTION)
            dialog.right_button.clicked.connect(dialog.close)
            dialog.left_button.clicked.connect(lambda: self.__download_portable_version(dialog))

            dialog.exec()
        
        self.finished.emit()
            