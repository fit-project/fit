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

from PyQt5 import QtCore, QtGui, QtWidgets

from view.case_form import CaseForm


from controller.case import Case as CaseController
from common.constants.view.case import *

class Case(QtWidgets.QDialog):

    def __init__(self, case_info, parent=None):
        super(Case, self).__init__(parent)

        self.case_info = case_info

        self.setObjectName("Case")
        self.resize(479, 311)
        self.setWindowTitle(DIALOG_TITLE.format(self.case_info['name'], str(self.case_info['id'])))
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.initUI()
        self.__set_current_config_values()

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)
    
    def initUI(self):
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setGeometry(QtCore.QRect(10, 270, 441, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.button_box.setCenterButtons(False)
        self.button_box.setObjectName("save")
        self.form = CaseForm(self)

        
    def __set_current_config_values(self):
        self.form.set_index_from_case_id(self.case_info['id'])
        self.form.name.setEnabled(False)
        self.form.lawyer_name.setText(self.case_info['lawyer_name'])
        self.form.set_index_from_type_proceedings_id(self.case_info['proceeding_type'])
        self.form.courthouse.setText(self.case_info['courthouse'])
        self.form.proceeding_number.setText(str(self.case_info['proceeding_number']))


    def accept(self) -> None:
        self.case_info = self.form.get_current_case_info()
        CaseController().cases = self.case_info
        return super().accept()

    def reject(self) -> None:
        return super().reject()
