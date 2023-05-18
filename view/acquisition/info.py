#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

import os
from PyQt6 import QtGui, QtCore, QtWidgets

class AcquisitionInfo(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(AcquisitionInfo, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setObjectName("AcquisitionStatusView")
        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
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
        for column in range(self.table.columnCount()):
            item = self.table.item(row, column)
            if item is not None:
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable)

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