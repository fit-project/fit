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
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.sip import delete


class AcquisitionStatus(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AcquisitionStatus, self).__init__(parent)


    def setupUi(self):
        #self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        #self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setObjectName("AcquisitionStatusView")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(800, 400)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(5)
        self.setFont(font)
        self.setWindowTitle("Acquisition status")
        self.setWindowFilePath("")
        self.setModal(True)

        self.title = QtWidgets.QLabel(self)
        self.title.setMargin(15)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setText('No acquisition in progress!')


        self.vertical_layout_widget = QtWidgets.QWidget(self)
        self.vertical_layout_widget.setGeometry(QtCore.QRect(0, 0, 800, 400))
        self.vertical_layout_widget.setObjectName("verticalLayoutWidget")
        self.vertical_layout = QtWidgets.QVBoxLayout(self.vertical_layout_widget)
        self.vertical_layout.setContentsMargins(20, 40, 10, 20)
        self.vertical_layout.setSpacing(10)
        self.vertical_layout.setObjectName("verticalLayout")
    
        QtCore.QMetaObject.connectSlotsByName(self)
       

    def add_task(self, name):

        horizontal_layout = QtWidgets.QHBoxLayout()
        horizontal_layout.setContentsMargins(5, 0, 5, 0)
        horizontal_layout.setObjectName(name.title().replace(" ", "") + 'HLayout')
    
        icon = QtWidgets.QLabel(self.vertical_layout_widget)
        icon.setObjectName(name.title().replace(" ", "") + 'Icon')
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        icon.setFont(font)
        

        horizontal_layout.addWidget(icon)

        task_name = QtWidgets.QLabel(self.vertical_layout_widget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        task_name.setFont(font)
        task_name.setText(name + ':')
    
        horizontal_layout.addWidget(task_name)

        status = QtWidgets.QLabel(self.vertical_layout_widget)
        status.setObjectName(name.title().replace(" ", "") + 'Status')
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        status.setFont(font)
 
        horizontal_layout.addWidget(status)
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        horizontal_layout.addItem(spacer)

        self.vertical_layout.addLayout(horizontal_layout)

        #remove spacer before insert it
        index = self.vertical_layout.count()
        while(index >= 0):
            item = self.vertical_layout.itemAt(index)
            if isinstance(item, QtWidgets.QSpacerItem):
                self.vertical_layout.removeItem(item)
            index -=1
        
        bottom_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vertical_layout.addItem(bottom_spacer)

    def set_status(self, name, msg, status):
        status_msg_lbl = self.findChild(QtWidgets.QLabel, name.title().replace(" ", "") + 'Status')
        if status_msg_lbl is not None:
            status_msg_lbl.setText(msg)

        icon = self.findChild(QtWidgets.QLabel, name.title().replace(" ", "") + 'Icon')
        if icon is not None:
            pixmap = QtGui.QPixmap(os.path.join('assets/images', 'progress.png'))
            if status == 'done':
                pixmap = QtGui.QPixmap(os.path.join('assets/images', 'done.png'))
            
            icon.setPixmap(pixmap)

    def set_title(self, title):
        self.title.setText(title)
        self.title.adjustSize()

    def clear(self):
        children = self.children()
        for child in children:
                delete(child)
        self.setupUi()