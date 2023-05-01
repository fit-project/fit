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
from PyQt5 import QtGui, QtCore, QtWidgets

class AcquisitionInfo(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AcquisitionInfo, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setObjectName("AcquisitionStatusView")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.icon =  QtGui.QIcon(os.path.join('assets/svg/acquisition', 'info-circle.svg'))

        self.table = QtWidgets.QTableWidget(self)
        
        self.table.resize(500, 400)
      
        self.table.setColumnCount(3)
        self.table.setColumnWidth(0, 250)


        # Set the table headers
        self.table.setHorizontalHeaderLabels(["Task", "State", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)

    def add_task(self, task, state, status, details=""):
        row = self.table.rowCount()
        self.table.insertRow(row)
        status = QtWidgets.QTableWidgetItem(status)

        if details:
            status.setIcon(self.icon)
    
        status.setToolTip(details)
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(task))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(state))
        self.table.setItem(row, 2, status)
    
    def clear_info(self):
        self.table.clearContents()
        self.table.setRowCount(0)
    
    def update_task(self, row, state, status, details):
        self.__update_task_state(row, state)
        self.__update_task_status(row, status, details)

        self.table.update()
        
    def __update_task_state(self, row, state):
        self.table.item(row, 1).setText(state)
    
    def __update_task_status(self, row, status, details):
        item = self.table.item(row, 2)

        if details:
            if item.icon().isNull():
                item.setIcon(self.icon)
        else:
             if item.icon().isNull() is False:
                 item.setIcon(QtGui.QIcon())

        item.setToolTip(details)
        item.setText(status)
    
    def get_row(self, task):
        row = None
        for i in range(self.table.rowCount()):
           if self.table.item(i, 0).text() == task:
               row = i
               break
           
        return row