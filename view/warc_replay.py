#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
#
# Copyright (c) 2022 FIT-Project and others
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


import shutil

from PyQt5 import QtGui
from PyQt5.QtWidgets import QFileDialog

from scapy.all import *

from PyQt5.QtCore import QThread, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

from view.case import Case as CaseView
from view.configuration import Configuration as ConfigurationView

from controller.warc_replay import WarcReplay as WarcReplayController

logger_acquisition = logging.getLogger(__name__)
logger_hashreport = logging.getLogger('hashreport')
logger_whois = logging.getLogger('whois')
logger_headers = logging.getLogger('headers')
logger_nslookup = logging.getLogger('nslookup')

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *


class WarcReplay(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(WarcReplay, self).__init__(*args, **kwargs)

        self.browser = QWebEngineView()
        self.acquisition_directory = None

    def init(self, case_info):
        self.case_info = case_info
        self.case_view = CaseView(self.case_info, self)
        self.case_view.hide()
        self.configuration_view = ConfigurationView(self)
        self.configuration_view.hide()
        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")
        self.replay()
        self.setCentralWidget(self.browser)
        self.setWindowTitle("Freezing Internet Tool")
        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))
        self.showMaximized()

    def replay(self):
        # start the server
        self.server_thread = WarcReplayController()
        self.server_thread.finished.connect(self.server_thread_finished)
        self.server_thread.start()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        open_folder = self.get_current_dir()

        filename, _ = QFileDialog.getOpenFileName(self, "Seleziona il file warc o wacz", open_folder,
                                                  "WARC and WACZ Files (*.warc *.wacz)", options=options)
        if filename:
            self.load_warc(filename)

    def load_warc(self, filename):
        # copy the file in a temp folder
        origin = filename
        destination = "warc_player/cache/"
        shutil.copy(origin, destination)

        # prepare the url with the file path
        url = QUrl(f'http://localhost:8000/warc_player/webrecorder_player.html?file=cache/{os.path.basename(filename)}')
        self.browser.setUrl(url)


    def get_current_dir(self):
        if not self.acquisition_directory:
            configuration_general = self.configuration_view.get_tab_from_name("configuration_general")
            open_folder = os.path.expanduser(
                os.path.join(configuration_general.configuration['cases_folder_path'], self.case_info['name']))
            return open_folder
        else:
            return self.acquisition_directory

    def server_thread_finished(self):
        self.server_thread.quit()
        self.server_thread.wait()

    def closeEvent(self, event):
        destination = "warc_player/cache"
        for root, dirs, files in os.walk(destination):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        self.server_thread.stop_server = True
