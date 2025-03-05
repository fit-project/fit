#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
from urllib.parse import urlparse

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest


class WebEngineProfile(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(WebEngineProfile, cls).__new__(cls)
            profile = QWebEngineProfile.defaultProfile()
            cls.default_download_path = profile.downloadPath()
            profile.clearAllVisitedLinks()
            cookie_store = profile.cookieStore()
            cookie_store.deleteAllCookies()

        return cls.instance


class WebEnginePage(QWebEnginePage):
    new_page_after_link_with_target_blank_attribute = pyqtSignal(QWebEnginePage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__default_profile = WebEngineProfile()

    def handleCertificateError(self, error):
        error.acceptCertificate()

    # When you click a link that has the target="_blank" attribute, QT calls the CreateWindow method in
    # QWebEnginePage to create a new tab/new window.
    def createWindow(
        self,
        _type,
    ):
        page = WebEnginePage(self)
        page.profile().setDownloadPath(self.profile().downloadPath())
        self.new_page_after_link_with_target_blank_attribute.emit(page)
        return page

    def reset_default_path(self):
        self.profile().setDownloadPath(self.__default_profile.default_download_path)


class WebEngineView(QWebEngineView):
    saveResourcesFinished = pyqtSignal()
    downloadItemFinished = pyqtSignal(QWebEngineDownloadRequest)
    downloadProgressChanged = pyqtSignal(int, int)
    downloadStarted = pyqtSignal(QWebEngineDownloadRequest)
    downloadError = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def set_download_request_handler(self):
        self.page().profile().downloadRequested.connect(self.__handle_download_request)

    def set_acquisition_dir(self, acquisition_directory):
        default_download_path = os.path.join(acquisition_directory, "downloads")
        if not os.path.isdir(default_download_path):
            os.makedirs(default_download_path)

        self.page().profile().setDownloadPath(default_download_path)

    def save_resources(self, acquisition_page_folder):
        hostname = urlparse(self.url().toString()).hostname
        if not hostname:
            hostname = "unknown"

        self.page().save(
            os.path.join(acquisition_page_folder, hostname + ".html"),
            format=QWebEngineDownloadRequest.SavePageFormat.CompleteHtmlSaveFormat,
        )

    def __handle_download_request(self, download):

        if download.isSavePageDownload():
            download.isFinishedChanged.connect(self.saveResourcesFinished.emit)

        else:
            self.downloadStarted.emit(download)

            download.receivedBytesChanged.connect(
                lambda: self.downloadProgressChanged.emit(
                    download.receivedBytes(),
                    download.totalBytes(),
                )
            )
            download.totalBytesChanged.connect(
                lambda: self.downloadProgressChanged.emit(
                    download.receivedBytes(),
                    download.totalBytes(),
                )
            )

            download.isFinishedChanged.connect(
                lambda: self.downloadItemFinished.emit(download)
            )

            download.accept()

    def closeEvent(self, event):
        self.page().profile().clearHttpCache()
