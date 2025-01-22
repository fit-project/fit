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

from PyQt6 import QtCore, QtWidgets

from view.checks.check import Check

from view.dialog import Dialog, DialogButtonTypes
from view.error import Error as ErrorView
from view.checks.download_and_save import DownloadAndSave

from common.utility import is_npcap_installed, get_npcap_installer_url, get_platform
from common.constants.view.tasks import status
from common.constants.view.initial_checks import (
    NPCAP,
    WAR_NPCAP_NOT_INSTALLED,
    NPCAP_DOWNLOAD,
    ERR_NPCAP_RELEASE_VERSION,
    NPCAP_ERROR_DURING_INSTALLATION,
)


class NpcapInstalledCheck(Check):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.donwload_and_save = None

    def run_check(self):
        if get_platform() == "win":
            # Check if NPCAP is installed
            if is_npcap_installed() is False:
                dialog = Dialog(
                    NPCAP,
                    WAR_NPCAP_NOT_INSTALLED,
                )
                dialog.message.setStyleSheet("font-size: 13px;")
                dialog.set_buttons_type(DialogButtonTypes.QUESTION)
                dialog.right_button.clicked.connect(lambda: self.__not_install(dialog))
                dialog.left_button.clicked.connect(
                    lambda: self.__download_npcap(dialog)
                )

                dialog.exec()
            else:
                self.finished.emit(status.SUCCESS)
        else:
            self.finished.emit(status.SUCCESS)

    def __not_install(self, dialog=None):
        if dialog:
            dialog.close()
        if  self.donwload_and_save is not None:
            self.donwload_and_save.close()
        self.finished.emit(status.FAIL)

    def __download_npcap(self, dialog=None):
        if dialog:
            dialog.close()
        try:
            url = get_npcap_installer_url()

            self.ncap_process_name = QtCore.QUrl(url).path().split("/")[-1]

            self.donwload_and_save = DownloadAndSave(url, NPCAP, NPCAP_DOWNLOAD)
            self.donwload_and_save.rejected.connect(self.__not_install)
            self.donwload_and_save.finished.connect(self.__install_ncap)
            self.donwload_and_save.exec()
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
            self.__not_install()
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

        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"] == self.ncap_process_name:
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
            self.__not_install()
        else:
            self.finished.emit(status.SUCCESS)
            self.donwload_and_save.close()
