#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QFileDialog

from view.clickable_label import ClickableLabel as ClickableLabelView


from view.configurations.tabs.general.typesproceedings import TypesProceedings as TypesproceedingsView
from controller.configurations.tabs.general.general import General as GeneralController

from common.constants.view.configurations import general


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
      self.group_box_cases_folder.setGeometry(QtCore.QRect(10, 30, 691, 51))
      self.group_box_cases_folder.setObjectName("group_box_cases_folder")
      self.cases_folder = QtWidgets.QLineEdit(self.group_box_cases_folder)
      self.cases_folder.setGeometry(QtCore.QRect(20, 20, 601, 22))
      self.cases_folder.setObjectName("cases_folder_path")
      self.tool_button_cases_folder = QtWidgets.QToolButton(self.group_box_cases_folder)
      self.tool_button_cases_folder.setGeometry(QtCore.QRect(640, 20, 27, 22))
      self.tool_button_cases_folder.setObjectName("tool_button_cases_folder")
      self.tool_button_cases_folder.clicked.connect(self.__select_cases_folder)

      #HOME PAGE
      self.group_box_home_page_url = QtWidgets.QGroupBox(self)
      self.group_box_home_page_url.setGeometry(QtCore.QRect(10, 90, 691, 51))
      self.group_box_home_page_url.setObjectName("group_box_home_page_url")
      self.home_page_url = QtWidgets.QLineEdit(self.group_box_home_page_url)
      self.home_page_url.setGeometry(QtCore.QRect(20, 20, 601, 22))
      self.home_page_url.setObjectName("home_page_url")

      # USER AGENT
      self.group_box_user_agent = QtWidgets.QGroupBox(self)
      self.group_box_user_agent.setGeometry(QtCore.QRect(10, 150, 691, 80))
      self.group_box_user_agent.setObjectName("group_box_user_agent")

      self.label_user_agent_site = ClickableLabelView(general.USER_AGENT_SITE, self.group_box_user_agent)
      self.label_user_agent_site.setGeometry(QtCore.QRect(20, 20, 500, 22))
      self.label_user_agent_site.setObjectName("label_two_factor_auth")

      self.user_agent = QtWidgets.QLineEdit(self.group_box_user_agent)
      self.user_agent.setGeometry(QtCore.QRect(20, 42, 601, 22))
      self.user_agent.setObjectName("user_agent")

      self.button_default_user_agent = QtWidgets.QToolButton(self.group_box_user_agent)
      self.button_default_user_agent.setGeometry(QtCore.QRect(625, 42, 60, 22))
      self.button_default_user_agent.setObjectName("button_default_user_agent")
      self.button_default_user_agent.clicked.connect(self.__default_user_agent)

      

      
        
      #PROCEEDINGS TYPE LIST
      self.group_box_types_proceedings = TypesproceedingsView(self)




   def retranslateUi(self):
      self.setWindowTitle(general.GENERAL)
      self.group_box_cases_folder.setTitle(general.CASE_FOLDER)
      self.tool_button_cases_folder.setText("...")
      self.group_box_home_page_url.setTitle(general.HOME_URL)
      self.group_box_user_agent.setTitle(general.USER_AGENT)
      self.button_default_user_agent.setText(general.RESET)
      self.label_user_agent_site.setText(general.USER_AGENT_SITE_LABEL)

   def __select_cases_folder(self):
        cases_folder = QtWidgets.QFileDialog.getExistingDirectory(self,
                       'Select Cases Folder', 
                       os.path.expanduser(self.cases_folder.text()),
                       QFileDialog.Option.ShowDirsOnly)
        self.cases_folder.setText(cases_folder)

   def __default_user_agent(self):
      self.user_agent.setText(general.DEFAULT_USER_AGENT)

   def __set_current_config_values(self):
      self.cases_folder.setText(self.configuration['cases_folder_path'])
      self.home_page_url.setText(self.configuration['home_page_url'])
      self.user_agent.setText(self.configuration['user_agent'])
   
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