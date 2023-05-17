#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

from PyQt6 import QtCore, QtGui, QtWidgets

import sys
import re


import view.configurations
import pkgutil
from inspect import isclass
from importlib import import_module

class Configuration(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(Configuration, self).__init__(parent)

        self.setObjectName("ConfigurationView")
        self.resize(722, 480)

        #self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.setGeometry(QtCore.QRect(0, 0, 721, 431))
        self.tabs.setObjectName("tabs")

        self.load_tabs()
        self.retranslateUi()

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(520, 440, 192, 28))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Save)

        self.buttonBox.setObjectName("buttonBox")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Configuration", "Fit Configuration"))


    def load_tabs(self):
        package=view.configurations
        class_names_modules = {}
        for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__, prefix=package.__name__+'.', onerror=lambda x: None):


            #import module if not loaded
            if modname not in sys.modules and not ispkg:
                import_module(modname)

            if modname in sys.modules and not ispkg:
                
                #find class name in a module 
                class_name = [x for x in dir(sys.modules[modname]) if isclass(getattr(sys.modules[modname], x)) and 
                                getattr(sys.modules[modname], '__is_tab__') and x.lower() == modname.rsplit( ".", 1 )[ 1 ]]

                if class_name:

                    class_names_modules.setdefault(class_name[0], []).append(sys.modules[modname])

        ordered_keys = sorted(class_names_modules.keys())
        for key in ordered_keys:
            for value in class_names_modules[key]:
                tab = getattr(value, key)
                tab = tab()
                self.tabs.addTab(tab, tab.windowTitle())
    
    def accept(self) -> None:
        for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)
            tab.accept()

        return super().accept()
    
    def get_tab_from_name(self, name):
         for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)

            if tab.objectName() == name:
                return tab

    
    def reject(self) -> None:
        for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)
            tab.reject()
            
        return super().reject()