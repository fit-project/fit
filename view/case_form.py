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


from view.error import Error as ErrorView

from controller.case import Case as CaseController
from controller.configurations.tabs.general.typesproceedings import TypesProceedings as TypesProceedingsController

from common.error import ErrorMessage


class CaseForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CaseForm, self).__init__(parent)

        error_msg = ErrorMessage()
        self.controller = CaseController()
        self.cases = self.controller.cases
        self.proceedings = TypesProceedingsController().proceedings

        self.setGeometry(QtCore.QRect(40, 30, 401, 202))
        self.setObjectName("form_layout")


        self.initUI()
        self.retranslateUi()
        self.__set_current_config_values()

    def initUI(self):
        self.case_form_layout = QtWidgets.QFormLayout(self)
        self.case_form_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.case_form_layout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.case_form_layout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.case_form_layout.setContentsMargins(9, 13, 0, 13)
        self.case_form_layout.setVerticalSpacing(10)
        self.case_form_layout.setObjectName("case_form_layout")

        #CASE_NAME_COMBO
        self.name_label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.name_label.setFont(font)
        self.name_label.setObjectName("name_label")
        self.case_form_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.name_label)
        self.name = QtWidgets.QComboBox(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.name.setFont(font)
        self.name.setObjectName("name")
        self.case_form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.name)

        

        #LAWYER_NAME_LINE_EDIT
        self.lawyer_name_label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lawyer_name_label.setFont(font)
        self.lawyer_name_label.setObjectName("lawyer_name_label")
        self.case_form_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lawyer_name_label)
        self.lawyer_name = QtWidgets.QLineEdit(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lawyer_name.setFont(font)
        self.lawyer_name.setObjectName("lawyer_name")
        self.case_form_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lawyer_name)


        #types_proceedings_COMBO
        self.types_proceedings_label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.types_proceedings_label.setFont(font)
        self.types_proceedings_label.setObjectName("types_proceedings_id_label")
        self.case_form_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.types_proceedings_label)
        self.types_proceedings = QtWidgets.QComboBox(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.types_proceedings.setFont(font)
        self.types_proceedings.setObjectName("types_proceedings_id")        
        self.case_form_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.types_proceedings)


        #COURTHOUSE_LINE_EDIT
        self.courthouse_label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.courthouse_label.setFont(font)
        self.courthouse_label.setObjectName("courthouse_label")
        self.case_form_layout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.courthouse_label)
        self.courthouse = QtWidgets.QLineEdit(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.courthouse.setFont(font)
        self.courthouse.setObjectName("courthouse")
        self.case_form_layout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.courthouse)


        #PROCEEDINGS_NUMBER_LINE_EDIT
        self.proceedings_number_label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.proceedings_number_label.setFont(font)
        self.proceedings_number_label.setObjectName("proceedings_number_label")
        self.case_form_layout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.proceedings_number_label)
        self.proceedings_number = QtWidgets.QLineEdit(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.proceedings_number.setFont(font)
        self.proceedings_number.setObjectName("proceedings_number")
        self.case_form_layout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.proceedings_number)

        self.retranslateUi()


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("CaseForm", "Dialog"))
        self.name_label.setText(_translate("CaseForm", "Cliente/Caso*"))
        self.lawyer_name_label.setText(_translate("CaseForm", "Avvocato"))
        self.types_proceedings_label.setText(_translate("CaseForm", "Tipo procedimento"))
        self.courthouse_label.setText(_translate("CaseForm", "Tribunale"))
        self.proceedings_number_label.setText(_translate("CaseForm", "Numero Procedimento"))
    

    def set_index_from_type_proceedings_id(self, type_proceedings_id):
        self.types_proceedings.setCurrentIndex(self.types_proceedings.findData(type_proceedings_id))
    
    def set_index_from_case_id(self, case_id):
        self.name.setCurrentIndex(self.name.findData(case_id))
    

    def __set_current_config_values(self):

        for case in self.cases:
            self.name.addItem(case['name'], case['id'])

        for proceedings in self.proceedings:
            self.types_proceedings.addItem(proceedings['name'], proceedings['id'])
    
    def get_current_case_info(self):

        case_info = next((item for item in self.cases if item["name"] == self.name.currentText()), {})
        
        for keyword in self.controller.keys:
            item = self.findChild(QtCore.QObject, keyword)
            if item is not None:
                if isinstance(item, QtWidgets.QComboBox):
                    if keyword in 'types_proceedings_id': 
                        item= item.currentData()
                    else:
                        item= item.currentText()
                elif isinstance(item, QtWidgets.QLineEdit) is not False:
                    if item.text():
                        item = item.text()
                    else:
                        item = None

                case_info[keyword] = item

        return case_info
