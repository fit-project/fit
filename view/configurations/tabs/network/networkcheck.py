#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

from PyQt6 import QtCore, QtGui, QtWidgets

from controller.configurations.tabs.network.networkcheck import NetworkControllerCheck as NetworkCheckController
from common.constants.view.network import *

__is_tab__ = False

class NetworkCheck(QtWidgets.QGroupBox):

  def __init__(self, parent=None):

    super(NetworkCheck, self).__init__(parent)

    self.controller = NetworkCheckController()
    self.configuration = self.controller.configuration

    self.initUI()
    self.retranslateUi()
    self.__set_current_config_values()
    

  def initUI(self):

    self.setGeometry(QtCore.QRect(10, 195, 691, 101))
    self.setObjectName("group_box_network_check")

    #NTP GROUPBOX
    self.group_box_ntp_configuration = QtWidgets.QGroupBox(self)
    self.group_box_ntp_configuration.setGeometry(QtCore.QRect(10, 30, 251, 51))

    #NTP SERVER 
    self.group_box_ntp_configuration.setObjectName("group_box_ntp_configuration")
    self.ntp_server = QtWidgets.QLineEdit(self.group_box_ntp_configuration)
    self.ntp_server.setGeometry(QtCore.QRect(20, 20, 211, 22))
    self.ntp_server.setObjectName("ntp_server")

    #NSLOOKUP GROUPBOX 
    self.group_box_nslookup_configuration = QtWidgets.QGroupBox(self)
    self.group_box_nslookup_configuration.setGeometry(QtCore.QRect(280, 30, 371, 51))
    self.group_box_nslookup_configuration.setObjectName("group_box_nslookup_configuration")

    #NSLOOKUP DNS SERVER 
    self.nslookup_dns_server = QtWidgets.QLineEdit(self.group_box_nslookup_configuration)
    self.nslookup_dns_server.setGeometry(QtCore.QRect(10, 20, 151, 22))
    self.nslookup_dns_server.setObjectName("nslookup_dns_server")

    #NSLOOKUP ENABLE TCP 
    self.nslookup_enable_tcp = QtWidgets.QCheckBox(self.group_box_nslookup_configuration)
    self.nslookup_enable_tcp.setGeometry(QtCore.QRect(180, 20, 81, 17))
    palette = QtGui.QPalette()
    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
    brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
    #palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
    brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
    #palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
    brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
    brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
    #palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
    self.nslookup_enable_tcp.setPalette(palette)
    self.nslookup_enable_tcp.setObjectName("nslookup_enable_tcp")

    #NSLOOKUP ENABLE VERBOSE MODE
    self.nslookup_enable_verbose_mode = QtWidgets.QCheckBox(self.group_box_nslookup_configuration)
    self.nslookup_enable_verbose_mode.setGeometry(QtCore.QRect(270, 20, 81, 17))
    palette = QtGui.QPalette()
    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
    brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
    palette.setBrush(QtGui.QPalette.ColorGroup.Active,QtGui.QPalette.ColorRole.WindowText, brush)
    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
    brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
    palette.setBrush(QtGui.QPalette.ColorGroup.Inactive, QtGui.QPalette.ColorRole.WindowText, brush)
    brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
    brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
    palette.setBrush(QtGui.QPalette.ColorGroup.Disabled,QtGui.QPalette.ColorRole.WindowText, brush)
    self.nslookup_enable_verbose_mode.setPalette(palette)
    self.nslookup_enable_verbose_mode.setChecked(True)
    self.nslookup_enable_verbose_mode.setObjectName("nslookup_enable_verbose_mode")

      
  
  def retranslateUi(self):
    self.setTitle(GROUP_BOX_TITLE_NETWORK_CHECK)
    self.group_box_ntp_configuration.setTitle(GROUP_BOX_TITLE_NTP)
    self.group_box_nslookup_configuration.setTitle(GROUP_BOX_TITLE_NSLOOKUP)
    self.nslookup_dns_server.setPlaceholderText(DNS)
    self.nslookup_enable_tcp.setText(NSLOOKUP_OPTIONS_ENABLE_TCP)
    self.nslookup_enable_verbose_mode.setText(NSLOOKUP_OPTIONS_ENABLE_VERBOSE_MODE)

  
  def __set_current_config_values(self):
    self.ntp_server.setText(self.configuration['ntp_server'])
    self.nslookup_dns_server.setText(self.configuration['nslookup_dns_server'])
    self.nslookup_enable_tcp.setChecked(self.configuration['nslookup_enable_tcp'])
    self.nslookup_enable_verbose_mode.setChecked(self.configuration['nslookup_enable_verbose_mode'])

  def __get_current_values(self):

      for keyword in self.configuration:
         item = self.findChild(QtCore.QObject, keyword)

         if item is not None:
            if isinstance(item, QtWidgets.QLineEdit) is not False and item.text():
               item = item.text()
            elif isinstance(item, QtWidgets.QCheckBox):
                    item = item.isChecked()

            self.configuration[keyword] = item


  def accept(self) -> None:
    self.__get_current_values()
    self.controller.configuration = self.configuration
  
  def reject(self) -> None:
    pass

