#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

from PyQt6 import QtCore, QtWidgets


from view.configurations.tabs.screenrecorder.codec import Codec as CodecView
from controller.configurations.tabs.screenrecorder.screenrecorder import ScreenRecorder as ScreenRecorderController

__is_tab__ = True

class ScreenRecorder(QtWidgets.QWidget):

   def __init__(self, parent=None):

      super(ScreenRecorder, self).__init__(parent)

      self.controller = ScreenRecorderController()
      self.options = self.controller.options

      self.setObjectName("configuration_screenrecorder")

      self.initUI()
      self.retranslateUi()
      self.__set_current_config_values()

   def initUI(self):
       #ENABLE CHECKBOX
        self.enabled_checkbox = QtWidgets.QCheckBox("Enable Screen Recorder", self)
        self.enabled_checkbox.setGeometry(QtCore.QRect(10, 30, 270, 70))
        self.enabled_checkbox.stateChanged.connect(self._is_enabled_screen_recorder)
        self.enabled_checkbox.setObjectName("enabled")
        
        
        #FPS
        self.group_box_fps = QtWidgets.QGroupBox(self)
        self.group_box_fps.setGeometry(QtCore.QRect(10, 90, 160, 70))
        self.group_box_fps.setObjectName("group_box_fps")
        self.fps = QtWidgets.QSpinBox(self.group_box_fps)
        self.fps.setGeometry(QtCore.QRect(20, 30, 80, 22))
        self.fps.setObjectName("fps")
        
        
        #CODEC
        self.group_box_codec = CodecView(self)
        self.group_box_codec.codec.setObjectName('codec_id')


        #FILE NAME
        self.group_box_filename = QtWidgets.QGroupBox(self)
        self.group_box_filename.setGeometry(QtCore.QRect(10, 190, 661, 91))
        self.group_box_filename.setObjectName("group_box_filename_sr")
        self.filename = QtWidgets.QLineEdit(self.group_box_filename)
        self.filename.setGeometry(QtCore.QRect(20, 40, 601, 22))
        self.filename.setObjectName("filename")



   def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Codec", "Screen Recorder Options"))
        self.group_box_fps.setTitle(_translate("ConfigurationView", "Frame per Second (fps)"))
        self.group_box_filename.setTitle(_translate("ConfigurationView", "File Name"))


   def _is_enabled_screen_recorder(self):
        self.group_box_fps.setEnabled(self.enabled_checkbox.isChecked())
        self.group_box_codec.setEnabled(self.enabled_checkbox.isChecked())
        self.group_box_filename.setEnabled(self.enabled_checkbox.isChecked())

   def __set_current_config_values(self):
        self.enabled_checkbox.setChecked(self.options['enabled'])
        self.fps.setValue(self.options['fps'])
        self.group_box_codec.set_index_from_codec_id(self.options['codec_id'])
        self.filename.setText(self.options['filename'])

        self._is_enabled_screen_recorder()

   def __get_current_values(self):
        for keyword in self.options:
            item = self.findChild(QtCore.QObject, keyword)

            if item is not None:
                if isinstance(item, QtWidgets.QComboBox) is not False and item.currentData():
                    item = item.currentData()
                elif isinstance(item, QtWidgets.QLineEdit) is not False and item.text():
                    item = item.text()
                elif isinstance(item, QtWidgets.QSpinBox) is not False and item.value():
                    item = item.value()
                elif isinstance(item, QtWidgets.QCheckBox):
                    item = item.isChecked()

                self.options[keyword] = item

   def accept(self) -> None:
        self.__get_current_values()
        self.controller.options = self.options
    
   def reject(self) -> None:
        pass