#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
# 
# Copyright (c) 2023 FIT-Project and others
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
###### 

import os

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets

from view.error import Error as ErrorView

from common.utility import *
from common.constants.view.init import *

class DownloadAndInstallNpcap(QtWidgets.QDialog):

    def __init__(self, url, parent=None):
        super(DownloadAndInstallNpcap, self).__init__(parent)

        self.path = None
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.resize(255, 77)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)

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

    @QtCore.pyqtSlot("QWebEngineDownloadItem*")
    def on_download_requested(self, download):
        old_path = download.url().path()
        suffix = QtCore.QFileInfo(old_path).suffix()
        self.path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", old_path, "*." + suffix
        )
        if self.path:
            download.setPath(self.path)
            download.accept()
            download.finished.connect(self.__install)
            download.downloadProgress.connect(self.__progress)

    def __install(self):
        self.close()
        os.system('Powershell -Command Start-Process "{}" -Verb RunAs'.format(self.path))
        
    
    def __progress(self, bytes_received, bytes_total):
         if bytes_total > 0:
            download_percentage = int(bytes_received*100/bytes_total)
            self.progressBar.setValue(download_percentage)


class Init(QtCore.QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_check(self):
        #Check internet connection
        if check_internet_connection() is False:
            error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                            CHECK_CONNETION,
                            ERR_INTERNET_DISCONNECTED,
                            ''
                            )

            error_dlg.buttonClicked.connect(quit)
            error_dlg.exec_()
        
        # If os is win check 
        if get_platform() == 'win' :
            if is_npcap_installed() is False:
                try:
                    url = get_npcap_installer_url()
                    msg = QtWidgets.QMessageBox()
                    msg.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
                    msg.setWindowTitle(NPCAP)
                    msg.setText(WAR_NPCAP_NOT_INSTALLED)
                    msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    
                    return_value = msg.exec()
                    if return_value == QtWidgets.QMessageBox.Yes:
                        donwload_and_install = DownloadAndInstallNpcap(url)
                        donwload_and_install.exec_()

                except Exception as e:
                    error_dlg = ErrorView(QtWidgets.QMessageBox.Critical,
                            NPCAP,
                            ERR_NPCAP_RELEASE_VERSION,
                            str(e)
                            )
                    error_dlg.exec_()
        