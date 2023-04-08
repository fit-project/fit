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

        self.navigation_actions = ['back', 'forward', 'reload', 'home', 'close']
        self.acquisition_actions = ['start', 'stop', 'info']
        self.screenshot_actions = ['camera', 'select']

        back_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'back.svg')), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.setObjectName('back')
        back_btn.triggered.connect(parent.back)
        self.addAction(back_btn)

        next_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'forward.svg')), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.setObjectName('forward')
        next_btn.triggered.connect(parent.forward)
        self.addAction(next_btn)

        reload_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'reload.svg')),"Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.setObjectName('reload')
        reload_btn.triggered.connect(parent.reload)
        self.addAction(reload_btn)

        home_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'home.svg')), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.setObjectName('home')
        home_btn.triggered.connect(parent.navigate_home)
        self.addAction(home_btn)

        self.addSeparator()

        self.httpsicon = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(os.path.join('assets/svg/toolbar', 'lock-open.svg'))
        self.httpsicon.setPixmap(pixmap.scaled(16, 16, QtCore.Qt.KeepAspectRatio) )
        self.addWidget(self.httpsicon)

        self.urlbar = QtWidgets.QLineEdit()
        self.urlbar.returnPressed.connect(parent.navigate_to_url)

        #Set urlbar width seventy percent of primary screen
        self.urlbar.setMaximumWidth(QtGui.QGuiApplication.primaryScreen().geometry().width()*0.7)
        self.addWidget(self.urlbar)

        stop_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'close.svg')), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.setObjectName('close')
        stop_btn.triggered.connect(lambda: parent.tabs.currentWidget().stop())
        self.addAction(stop_btn)

        self.addSeparator()

        # START ACQUISITON ACTION
        self.start_acquisition_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'start.svg')), "Start Acquisition", self)
        self.start_acquisition_btn.setStatusTip("Start acquisition")
        self.start_acquisition_btn.triggered.connect(parent.start_acquisition)
        self.start_acquisition_btn.setObjectName('start')
        self.addAction(self.start_acquisition_btn)

        # STOP ACQUISITON ACTION
        self.stop_acquisition_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'stop-disabled.svg')), "Stop Acquisition", self)
        self.stop_acquisition_btn.setStatusTip("Stop acquisition")
        self.stop_acquisition_btn.triggered.connect(parent.stop_acquisition)
        self.stop_acquisition_btn.setObjectName('stop')
        self.stop_acquisition_btn.setEnabled(False)
        self.addAction(self.stop_acquisition_btn)

        # INFO ACQUISITON STATUS ACTION
        self.info_acquisition_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'info-disabled.svg')), "info Acquisition", self)
        self.info_acquisition_btn.setStatusTip("info acquisition")
        self.info_acquisition_btn.triggered.connect(parent._acquisition_status)
        self.info_acquisition_btn.setObjectName('info')
        self.info_acquisition_btn.setEnabled(False)
        self.addAction(self.info_acquisition_btn)

        self.addSeparator()

        # SCREENSHOT ACTION
        self.screenshot_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'camera-disabled.svg')), "Take a screenshot page", self)
        self.screenshot_btn.setObjectName('camera')
        self.screenshot_btn.setStatusTip("Take a full page screenshot")
        self.screenshot_btn.setEnabled(False)
    
        self.screenshot_btn.triggered.connect(parent.take_screenshot)
        self.addAction(self.screenshot_btn)

        # SCREENSHOT SELECTED AREA
        self.screenshot_sl_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'select-disabled.svg')), "Take a screenshot on the selected area", self)
        self.screenshot_sl_btn.setObjectName('select')
        self.screenshot_sl_btn.setStatusTip("Take a screenshot on the selected area")
        self.screenshot_sl_btn.setEnabled(False)
    
        self.screenshot_sl_btn.triggered.connect(parent.take_screenshot_selected_area)
        self.addAction(self.screenshot_sl_btn)

        # SCREENSHOT FULL PAGE
        self.screenshot_fp_btn = QtWidgets.QAction(QtGui.QIcon(os.path.join('assets/svg/toolbar', 'scroll-disabled.svg')), "Take a full page screenshot", self)
        self.screenshot_fp_btn.setObjectName('scroll')
        self.screenshot_fp_btn.setStatusTip("Take a full page screenshot")
        self.screenshot_fp_btn.setEnabled(False)
    
        self.screenshot_fp_btn.triggered.connect(parent.take_full_page_screenshot)
        self.addAction(self.screenshot_fp_btn)

        self.addSeparator()

    def enable_actions(self, filter=['all'], enabled=True):
        for action in self.actions():
            if action.objectName():
                if 'all' in filter or action.objectName() in filter:
                    if enabled:
                        icon = action.objectName() + '.svg'
                    else:
                       icon = action.objectName() + '-disabled.svg'

                    action.setIcon(QtGui.QIcon(os.path.join('assets/svg/toolbar', icon)))
                    action.setEnabled(enabled)
    
    def enable_start_acquisition_button(self, enabled=True):
        if enabled and self.parent().acquisition_is_started is not True:
             self.enable_actions(filter=['start'])
        else:
            self.enable_actions(filter=['start'], enabled=False)
    
    def enable_stop_and_info_acquisition_button(self, enabled=True):
        if enabled and self.parent().acquisition_is_started is True:
             self.enable_actions(filter=['stop', 'info'])
        else:
            self.enable_actions(filter=['stop', 'info'], enabled=False)
             
    def enable_screenshot_buttons(self, enabled=True):
        if enabled and self.parent().current_page_load_is_finished and self.parent().acquisition_is_started:
            self.enable_actions(filter=self.screenshot_actions)
        else:
            self.enable_actions(filter=self.screenshot_actions, enabled=False)