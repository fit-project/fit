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

from PyQt5 import QtCore, QtWidgets


from view.configurations.tabs.general.typesproceedings import TypesProceedings as TypesproceedingsView
from controller.configurations.tabs.general.general import General as GeneralController


import os

__is_tab__ = True

class General(QtWidgets.QWidget):

   def __init__(self, parent=None):

      super(General, self).__init__(parent)

      self.controller = GeneralController()
      self.configuration = self.controller.configuration

      self.setObjectName("configuration_general")

      self.initUI()
      self.retranslateUi()
      self.__set_current_config_values()

   def initUI(self):
      #CASES FOLDER
      self.group_box_cases_folder = QtWidgets.QGroupBox(self)
      self.group_box_cases_folder.setGeometry(QtCore.QRect(10, 30, 691, 91))
      self.group_box_cases_folder.setObjectName("group_box_cases_folder")
      self.cases_folder = QtWidgets.QLineEdit(self.group_box_cases_folder)
      self.cases_folder.setGeometry(QtCore.QRect(20, 40, 601, 22))
      self.cases_folder.setObjectName("cases_folder_path")
      self.tool_button_cases_folder = QtWidgets.QToolButton(self.group_box_cases_folder)
      self.tool_button_cases_folder.setGeometry(QtCore.QRect(640, 40, 27, 22))
      self.tool_button_cases_folder.setObjectName("tool_button_cases_folder")
      self.tool_button_cases_folder.clicked.connect(self.__select_cases_folder)



      #HOME PAGE
      self.group_box_home_page_url = QtWidgets.QGroupBox(self)
      self.group_box_home_page_url.setGeometry(QtCore.QRect(10, 140, 691, 91))
      self.group_box_home_page_url.setObjectName("group_box_home_page_url")
      self.home_page_url = QtWidgets.QLineEdit(self.group_box_home_page_url)
      self.home_page_url.setGeometry(QtCore.QRect(20, 40, 601, 22))
      self.home_page_url.setObjectName("home_page_url")
        
      #PROCEEDINGS TYPE LIST
      self.group_box_types_proceedings = TypesproceedingsView(self)



   def retranslateUi(self):
      _translate = QtCore.QCoreApplication.translate
      self.setWindowTitle(_translate("General", "General"))
      self.group_box_cases_folder.setTitle(_translate("General", "Cases Folder"))
      self.tool_button_cases_folder.setText(_translate("General", "..."))
      self.group_box_home_page_url.setTitle(_translate("General", "Home Page URL"))


   def __select_cases_folder(self):
        cases_folder = QtWidgets.QFileDialog.getExistingDirectory(self,
                       'Select Cases Folder', 
                       os.path.expanduser(self.cases_folder.text()),
                       QtWidgets.QFileDialog.ShowDirsOnly)
        self.cases_folder.setText(cases_folder)

   def __set_current_config_values(self):
      self.cases_folder.setText(self.configuration['cases_folder_path'])
      self.home_page_url.setText(self.configuration['home_page_url'])
   
   def __get_current_values(self):
        
      for keyword in self.configuration:
         item = self.findChild(QtCore.QObject, keyword)

         if item is not None:
            if isinstance(item, QtWidgets.QComboBox) is not False and item.currentText():
               item = item.currentText()
            elif isinstance(item, QtWidgets.QLineEdit) is not False and item.text():
               item = item.text()
            elif isinstance(item, QtWidgets.QPlainTextEdit) is not False and item.toPlainText():
               item = item.toPlainText()

            self.configuration[keyword] = item

   def accept(self) -> None:
      self.group_box_types_proceedings.accept()
      self.__get_current_values()
      self.controller.configuration = self.configuration
      

    
   def reject(self) -> None:
      pass