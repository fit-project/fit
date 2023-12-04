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
from PyQt6.QtWidgets import QFileDialog


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

    def handleCertificateError(self, error):
        error.acceptCertificate()

    # When you click a link that has the target="_blank" attribute, QT calls the CreateWindow method in
    # QWebEnginePage to create a new tab/new window.
    def createWindow(
        self,
        _type,
    ):
        page = WebEnginePage(self)
        self.new_page_after_link_with_target_blank_attribute.emit(page)
        return page


class WebEngineView(QWebEngineView):
    saveResourcesFinished = pyqtSignal()
    downloadItemFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.singleton = WebEngineProfile()

    def reconnect(self):
        self.selected_directory = self.singleton.default_download_path

        self.page().profile().setDownloadPath(self.selected_directory)
        self.page().profile().downloadRequested.connect(self.__retrieve_download_item)
        self.page().profile().downloadRequested.connect(self.__handle_download_request)

    def set_acquisition_dir(self, directory):
        self.acquisition_directory = directory
        self.selected_directory = os.path.join(self.acquisition_directory, "downloads")
        if not os.path.isdir(self.selected_directory):
            os.makedirs(self.selected_directory)
        self.page().profile().setDownloadPath(self.selected_directory)

    def write_html_to_file(html):
        with open("index.html", "w") as f:
            f.write(html)

    def save_resources(self, acquisition_page_folder):
        self.page().profile().downloadRequested.disconnect(
            self.__handle_download_request
        )
        hostname = urlparse(self.url().toString()).hostname
        if not hostname:
            hostname = "unknown"

        self.page().save(
            os.path.join(acquisition_page_folder, hostname + ".html"),
            format=QWebEngineDownloadRequest.SavePageFormat.CompleteHtmlSaveFormat,
        )

    def reconnect_signal(self):
        self.page().profile().downloadRequested.connect(self.__handle_download_request)

    def disconnect_signals(self):
        self.page().profile().downloadRequested.disconnect(
            self.__retrieve_download_item
        )
        self.page().profile().downloadRequested.disconnect(
            self.__handle_download_request
        )

    def __handle_download_request(self, download):
        if not os.path.isdir(self.selected_directory):
            self.selected_directory = self.singleton.default_download_path
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setDirectory(self.selected_directory)
        filename = download.downloadFileName()
        download.isFinishedChanged.connect(
            lambda: self.downloadItemFinished.emit(filename)
        )
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            self.selected_directory = file_dialog.selectedFiles()[0]
            download.accept()

    def __retrieve_download_item(self, download_item):
        download_item.isFinishedChanged.connect(self.saveResourcesFinished.emit)

    def closeEvent(self, event):
        self.page().profile().clearHttpCache()
