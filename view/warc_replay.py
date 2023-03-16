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
import os
import pathlib
import shutil

from PyQt5 import QtGui, QtWidgets
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

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *


class WarcReplay(QtWidgets.QMainWindow):
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
        self.replay()
        self.setCentralWidget(self.browser)
        self.showMaximized()

        # CONFIGURATION ACTION
        configuration_action = QtWidgets.QAction("Configuration", self)
        configuration_action.setStatusTip("Show configuration info")
        configuration_action.triggered.connect(self.configuration)
        self.menuBar().addAction(configuration_action)

        # CASE ACTION
        case_action = QtWidgets.QAction("Case", self)
        case_action.setStatusTip("Show case info")
        case_action.triggered.connect(self.case)
        self.menuBar().addAction(case_action)

        # REPLAY WARC
        replay_warc_action = QtWidgets.QAction("Replay", self)
        replay_warc_action.setStatusTip("Replay warc and wacz files")
        replay_warc_action.triggered.connect(self.replay)
        self.menuBar().addAction(replay_warc_action)

        self.configuration_general = self.configuration_view.get_tab_from_name("configuration_general")

        # Get network parameters for check (NTP, nslookup)
        self.configuration_network = self.configuration_general.findChild(QtWidgets.QGroupBox,
                                                                          'group_box_network_check')

        # Get timestamp parameters
        self.configuration_timestamp = self.configuration_view.get_tab_from_name("configuration_timestamp")

        self.show()

        self.setWindowTitle("Freezing Internet Tool")
        self.setWindowIcon(QtGui.QIcon(os.path.join('asset/images/', 'icon.png')))

    def replay(self):
        # start the server
        self.server_thread = WarcReplayController()
        port = self.server_thread.get_port()
        self.server_thread.finished.connect(self.server_thread_finished)
        self.server_thread.start()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        open_folder = self.get_current_dir()

        filename, _ = QFileDialog.getOpenFileName(self, "Seleziona il file warc o wacz", open_folder,
                                                  "WARC and WACZ Files (*.warc *.wacz)", options=options)
        if filename:
            self.load_warc(filename, port)

    def load_warc(self, filename,port):
        # copy the file in a temp folder
        origin = filename
        destination = "warc_player/cache/"
        directory_path = pathlib.Path(destination)
        if not directory_path.exists():
            directory_path.mkdir()
        shutil.copy(origin, destination)

        # prepare the url with the file path
        url = QUrl(f'http://localhost:{port}/warc_player/webrecorder_player.html?file=cache/{os.path.basename(filename)}')
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

    def case(self):
        self.case_view.exec_()

    def configuration(self):
        self.configuration_view.exec_()

    def closeEvent(self, event):
        destination = "warc_player/cache"
        for root, dirs, files in os.walk(destination):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        self.server_thread.stop_server = True
