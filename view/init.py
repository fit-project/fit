#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os

from PyQt6 import QtCore, QtWidgets, QtWebEngineWidgets, QtGui, uic

from view.error import Error as ErrorView
from view.dialog import Dialog, DialogButtonTypes
from view.clickable_label import ClickableLabel
from controller.configurations.tabs.packetcapture.packetcapture import PacketCapture
from controller.configurations.tabs.network.networktools import NetworkTools


from common.utility import *
from common.constants.view.init import *
from common.constants.view.general import *


class DownloadAndInstallNpcap(QtWidgets.QDialog):
    def __init__(self, url, parent=None):
        super(DownloadAndInstallNpcap, self).__init__(parent)

        self.path = None
        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.resize(255, 77)
        self.setWindowFlags(
            QtCore.Qt.WindowType.CustomizeWindowHint
            | QtCore.Qt.WindowType.WindowTitleHint
        )

        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 231, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.progressBar = QtWidgets.QProgressBar(self.horizontalLayoutWidget)
        self.progressBar.setObjectName("progressBar")
        self.horizontalLayout.addWidget(self.progressBar)

        self.setWindowTitle(NPCAP)
        self.label.setText(NPCAP_DOWNLOAD)

        self.web_view = QtWebEngineWidgets.QWebEngineView()
        self.web_view.page().profile().downloadRequested.connect(
            self.on_download_requested
        )

        self.web_view.load(QtCore.QUrl(url))
        self.web_view.hide()
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.web_view)

    # @QtCore.pyqtSlot("QWebEngineDownloadItem*")
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

    def __install(self):
        self.close()
        os.system(
            'Powershell -Command Start-Process "{}" -Verb RunAs'.format(self.path)
        )

    def __progress(self, bytes_received, bytes_total):
        if bytes_total > 0:
            download_percentage = int(bytes_received * 100 / bytes_total)
            self.progressBar.setValue(download_percentage)


class Init(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    def __quit(self):
        sys.exit(1)

    def __enable_functionality(self):
        configuration = NetworkTools().configuration
        if configuration.get("traceroute") is False:
            configuration["traceroute"] = True
            NetworkTools().configuration = configuration

        options = PacketCapture().options
        if options.get("enabled") is False:
            options["enabled"] = True
            PacketCapture().options = options

        self.__quit()

    def __disable_functionality(self, dialog=None):
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
                lambda: self.__disable_functionality(dialog)
            )
            dialog.left_button.clicked.connect(self.__enable_functionality)

            dialog.exec()

        # If os is win check
        if get_platform() == "win":
            if is_npcap_installed() is False:
                try:
                    url = get_npcap_installer_url()
                    msg = QtWidgets.QMessageBox()
                    msg.setWindowFlags(
                        QtCore.Qt.WindowType.CustomizeWindowHint
                        | QtCore.Qt.WindowType.WindowTitleHint
                    )
                    msg.setWindowTitle(NPCAP)
                    msg.setText(WAR_NPCAP_NOT_INSTALLED)
                    msg.setStandardButtons(
                        QtWidgets.QMessageBox.StandardButton.Yes
                        | QtWidgets.QMessageBox.StandardButton.No
                    )
                    msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)

                    return_value = msg.exec()
                    if return_value == QtWidgets.QMessageBox.StandardButton.Yes:
                        donwload_and_install = DownloadAndInstallNpcap(url)
                        donwload_and_install.exec()
                    else:
                        options = PacketCapture().options
                        options["enabled"] = False
                        PacketCapture().options = options

                except Exception as e:
                    error_dlg = ErrorView(
                        QtWidgets.QMessageBox.Icon.Critical,
                        NPCAP,
                        ERR_NPCAP_RELEASE_VERSION,
                        str(e),
                    )
                    error_dlg.exec()

        if getattr(sys, "frozen", False) and is_there_a_new_portable_version():

            dialog = QtWidgets.QDialog()
            uic.loadUi(resolve_path("ui/dialog/multipurpose.ui"), dialog)

            parser = ConfigParser()
            parser.read(resolve_path("assets/config.ini"))
            url = parser.get("fit_properties", "fit_latest_download_url")

            # HIDE STANDARD TITLE BAR
            dialog.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
            dialog.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

            # TITLE
            title = dialog.findChild(QtWidgets.QLabel, "titleRightInfo")
            title.setText(FIT_NEW_VERSION_TITLE)

            # CLOSE BUTTON
            close_app_button = dialog.findChild(QtWidgets.QPushButton, "closeButton")
            close_app_button.clicked.connect(dialog.close)

            # HIDE NAVIGATION BUTTON
            navigationButtons = dialog.findChild(QtWidgets.QFrame, "navigationButtons")
            navigationButtons.hide()

            # LAYOUT
            layout = dialog.findChild(QtWidgets.QVBoxLayout, "contentBoxLayout")

            # TEXT LABEL
            text = dialog.findChild(QtWidgets.QLabel, "text")

            text.setText(FIT_NEW_VERSION_MSG)
            label_url = ClickableLabel(url)
            label_url.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
            font = QtGui.QFont()
            font.setPointSize(18)
            label_url.setFont(font)
            label_url.setText(FIT_NEW_VERSION_DOWNLOAD)

            layout.addWidget(label_url)

            contentBox = dialog.findChild(QtWidgets.QFrame, "contentBox")
            contentBox.adjustSize()

            dialog.exec()
