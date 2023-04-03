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

from PyQt5 import QtCore, QtGui, QtWidgets

class NavigationToolBar(QtWidgets.QToolBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('NavigationToolBar')
        self.setIconSize(QtCore.QSize(25, 25))

        back_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/images', 'arrow-180.png')), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(parent.back)
        self.addAction(back_btn)

        next_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/images', 'arrow-000.png')), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(parent.forward)
        self.addAction(next_btn)

        reload_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/images', 'arrow-circle-315.png')),"Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(parent.reload)
        self.addAction(reload_btn)

        home_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/images', 'home.png')), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(parent.navigate_home)
        self.addAction(home_btn)

        self.addSeparator()

        self.httpsicon = QtWidgets.QLabel()
        self.httpsicon.setPixmap(QtGui.QPixmap(os.path.join('assets/images', 'lock-nossl.png')))
        self.addWidget(self.httpsicon)

        self.urlbar = QtWidgets.QLineEdit()
        self.urlbar.returnPressed.connect(parent.navigate_to_url)

        #Set urlbar width seventy percent of primary screen
        self.urlbar.setMaximumWidth(QtGui.QGuiApplication.primaryScreen().geometry().width()*0.8)
        self.addWidget(self.urlbar)

        stop_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/images', 'cross-circle.png')), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: parent.tabs.currentWidget().stop())
        self.addAction(stop_btn)

        self.addSeparator()

        # START ACQUISITON ACTION
        start_acquisition_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'start.svg')), "Start Acquisition", self)
        start_acquisition_btn.setStatusTip("Start acquisition")
        start_acquisition_btn.triggered.connect(parent.start_acquisition)
        start_acquisition_btn.setObjectName('StartAcquisitionActionToolBar')
        self.addAction(start_acquisition_btn)

        # STOP ACQUISITON ACTION
        stop_acquisition_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'stop-disabled.svg')), "Stop Acquisition", self)
        stop_acquisition_btn.setStatusTip("Stop acquisition")
        stop_acquisition_btn.triggered.connect(parent.stop_acquisition)
        stop_acquisition_btn.setObjectName('StopAcquisitionActionToolBar')
        stop_acquisition_btn.setEnabled(False)
        self.addAction(stop_acquisition_btn)

        # SCREENSHOT ACTION
        self.screenshot_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'camera-disabled.svg')), "Take a screenshot page", self)
        self.screenshot_btn.setObjectName('TakeScreenshotPageActionToolBar')
        self.screenshot_btn.setStatusTip("Take a full page screenshot")
        self.screenshot_btn.setEnabled(False)
    
        self.screenshot_btn.triggered.connect(parent.take_full_page_screenshot)
        self.addAction(self.screenshot_btn)
    
    def enable_screenshot_btn(self, enabled=True):

        if enabled and self.parent().current_page_load_is_finished and self.parent().acquisition_is_started:
            self.screenshot_btn.setIcon(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'camera.svg')))
            self.screenshot_btn.setEnabled(True)
        else:
            self.screenshot_btn.setIcon(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'camera-disabled.svg')))
            self.screenshot_btn.setEnabled(False)